from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import pandas as pd
from pydantic import BaseModel
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


class MLAnomalyResult(BaseModel):
    transactionId: str
    anomalyType: str
    anomalyScore: float
    severity: str
    modelConfidence: float
    explanation: str
    modelVersion: Optional[str] = None
    warnings: List[str] = []


class MLAnomalyDetectionModel:
    def __init__(
        self,
        model_version: str = "anomaly-model-v1",
        contamination: float = 0.05,
        min_training_records: int = 100,
        random_state: int = 42,
    ) -> None:
        self.model_version = model_version
        self.contamination = contamination
        self.min_training_records = min_training_records
        self.random_state = random_state
        self.pipeline: Optional[Pipeline] = None

        self.numeric_features = [
            "amount",
            "feeRate",
            "feeAmount",
            "clearingDelayDays",
        ]

        self.categorical_features = [
            "category",
            "paymentChannel",
            "threeDS",
            "mcc",
        ]

        self.required_features = self.numeric_features + self.categorical_features

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare anomaly model features safely.

        Numeric missing values are handled by SimpleImputer.
        Categorical missing values are converted to UNKNOWN.
        """

        prepared = df.copy()

        for feature in self.required_features:
            if feature not in prepared.columns:
                prepared[feature] = None

        for feature in self.categorical_features:
            prepared[feature] = prepared[feature].fillna("UNKNOWN").astype(str)

        return prepared[self.required_features]

    def train(self, training_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Train unsupervised anomaly model.

        No labels are required.
        The model learns normal portfolio behavior.
        """

        if len(training_df) < self.min_training_records:
            return {
                "trained": False,
                "warnings": [
                    f"Small dataset. Need at least {self.min_training_records} records."
                ],
            }

        X = self._prepare_features(training_df)

        numeric_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
            ]
        )

        categorical_transformer = Pipeline(
            steps=[
                ("encoder", OneHotEncoder(handle_unknown="ignore")),
            ]
        )

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_transformer, self.numeric_features),
                ("cat", categorical_transformer, self.categorical_features),
            ]
        )

        model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
        )

        self.pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", model),
            ]
        )

        self.pipeline.fit(X)

        return {
            "trained": True,
            "modelVersion": self.model_version,
            "metrics": {
                "trainingRows": len(training_df),
                "contamination": self.contamination,
            },
            "warnings": [],
        }

    def save(self, artifact_path: str) -> None:
        """
        Save trained anomaly model artifact.
        """

        if self.pipeline is None:
            raise ValueError("Cannot save model before training.")

        path = Path(artifact_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        joblib.dump(
            {
                "modelVersion": self.model_version,
                "pipeline": self.pipeline,
                "requiredFeatures": self.required_features,
            },
            path,
        )

    def load(self, artifact_path: str) -> None:
        """
        Load trained anomaly model artifact.
        """

        artifact = joblib.load(artifact_path)

        self.model_version = artifact["modelVersion"]
        self.pipeline = artifact["pipeline"]
        self.required_features = artifact["requiredFeatures"]

    def detect_batch(
        self,
        rows: List[Dict[str, Any]],
    ) -> List[MLAnomalyResult]:
        """
        Detect anomalies in batch.

        IsolationForest returns:
        - 1 for normal
        - -1 for anomaly
        """

        if self.pipeline is None:
            return []

        valid_rows = []
        warnings_by_transaction = {}

        for row in rows:
            transaction_id = str(row.get("transactionId", "UNKNOWN"))

            missing_features = [
                feature for feature in self.required_features if feature not in row
            ]

            if missing_features:
                warnings_by_transaction[transaction_id] = [
                    f"Missing required features: {missing_features}. Transaction skipped."
                ]
                continue

            valid_rows.append(row)

        if not valid_rows:
            return []

        df = self._prepare_features(pd.DataFrame(valid_rows))

        predictions = self.pipeline.predict(df)
        raw_scores = self.pipeline.decision_function(df)

        results = []

        for row, prediction, raw_score in zip(valid_rows, predictions, raw_scores):
            if prediction != -1:
                continue

            anomaly_score = round(float(abs(raw_score)), 4)
            severity = self._severity_from_score(anomaly_score)

            results.append(
                MLAnomalyResult(
                    transactionId=str(row.get("transactionId", "UNKNOWN")),
                    anomalyType="ML_ANOMALY",
                    anomalyScore=anomaly_score,
                    severity=severity,
                    modelConfidence=0.81,
                    modelVersion=self.model_version,
                    explanation=self._build_explanation(row),
                    warnings=warnings_by_transaction.get(
                        str(row.get("transactionId", "UNKNOWN")),
                        [],
                    ),
                )
            )

        return results

    def _severity_from_score(self, anomaly_score: float) -> str:
        """
        Convert anomaly score into severity.
        """

        if anomaly_score >= 0.15:
            return "HIGH"

        if anomaly_score >= 0.08:
            return "MEDIUM"

        return "LOW"

    def _build_explanation(self, row: Dict[str, Any]) -> str:
        """
        Provide a simple explanation for why the transaction may be unusual.
        """

        reasons = []

        if row.get("feeRate", 0) and row.get("feeRate", 0) > 1.85:
            reasons.append("fee rate is unusually high")

        if row.get("clearingDelayDays", 0) and row.get("clearingDelayDays", 0) >= 5:
            reasons.append("clearing delay is unusually long")

        if row.get("threeDS") is False and "Secure" in str(row.get("category", "")):
            reasons.append("3DS flag conflicts with secure category")

        if not reasons:
            reasons.append("transaction differs significantly from similar historical transactions")

        return "; ".join(reasons)