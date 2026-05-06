from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import pandas as pd
from pydantic import BaseModel
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


class RootCauseDriverEvidence(BaseModel):
    condition: str
    mlDriverScore: float
    confidence: str
    explanation: str
    modelVersion: Optional[str] = None
    warnings: List[str] = []


class RootCauseDriverModel:
    def __init__(
        self,
        model_version: str = "root-cause-model-v1",
        min_training_records: int = 100,
        high_loss_threshold: float = 5.0,
        random_state: int = 42,
    ) -> None:
        self.model_version = model_version
        self.min_training_records = min_training_records
        self.high_loss_threshold = high_loss_threshold
        self.random_state = random_state
        self.pipeline: Optional[Pipeline] = None
        self.feature_importance: Dict[str, float] = {}

        self.numeric_features = [
            "amount",
            "feeRate",
            "feeAmount",
            "clearingDelayDays",
            "expectedImpact",
            "historicalSuccessRate",
        ]

        self.categorical_features = [
            "category",
            "condition",
            "paymentChannel",
            "threeDS",
            "mcc",
            "suggestionType",
            "difficulty",
        ]

        self.required_features = self.numeric_features + self.categorical_features

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare training and prediction features safely.
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
        Train model to predict whether a transaction is high-loss.

        Uses label_actualSavings if available.
        If label_actualSavings >= high_loss_threshold, the row is treated as high-loss.
        """

        if len(training_df) < self.min_training_records:
            return {
                "trained": False,
                "warnings": [
                    f"Low data volume. Need at least {self.min_training_records} records."
                ],
            }

        if "label_actualSavings" not in training_df.columns:
            return {
                "trained": False,
                "warnings": ["Missing label_actualSavings column."],
            }

        df = training_df.dropna(subset=["label_actualSavings"]).copy()

        if len(df) < self.min_training_records:
            return {
                "trained": False,
                "warnings": ["Not enough labeled rows after removing missing labels."],
            }

        df["isHighLoss"] = (
            df["label_actualSavings"].astype(float) >= self.high_loss_threshold
        ).astype(int)

        if df["isHighLoss"].nunique() < 2:
            return {
                "trained": False,
                "warnings": ["No high-loss examples or no normal examples available."],
            }

        X = self._prepare_features(df)
        y = df["isHighLoss"]

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

        classifier = RandomForestClassifier(
            n_estimators=100,
            random_state=self.random_state,
        )

        self.pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", classifier),
            ]
        )

        self.pipeline.fit(X, y)
        self._extract_feature_importance()

        return {
            "trained": True,
            "modelVersion": self.model_version,
            "metrics": {
                "trainingRows": len(df),
                "highLossRows": int(df["isHighLoss"].sum()),
                "normalRows": int((df["isHighLoss"] == 0).sum()),
            },
            "warnings": [],
        }

    def _extract_feature_importance(self) -> None:
        """
        Extract feature importance from the trained random forest.

        For encoded categorical features, scores are grouped back to their base field.
        """

        if self.pipeline is None:
            self.feature_importance = {}
            return

        preprocessor = self.pipeline.named_steps["preprocessor"]
        model = self.pipeline.named_steps["model"]

        raw_feature_names = preprocessor.get_feature_names_out()
        raw_importances = model.feature_importances_

        grouped: Dict[str, float] = {}

        for raw_name, importance in zip(raw_feature_names, raw_importances):
            clean_name = raw_name

            if "__" in clean_name:
                clean_name = clean_name.split("__", 1)[1]

            base_name = clean_name.split("_", 1)[0]

            grouped[base_name] = grouped.get(base_name, 0.0) + float(importance)

        self.feature_importance = {
            key: round(value, 4)
            for key, value in grouped.items()
        }

    def save(self, artifact_path: str) -> None:
        """
        Save trained model and extracted feature importance.
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
                "featureImportance": self.feature_importance,
            },
            path,
        )

    def load(self, artifact_path: str) -> None:
        """
        Load model artifact.
        """

        artifact = joblib.load(artifact_path)

        self.model_version = artifact["modelVersion"]
        self.pipeline = artifact["pipeline"]
        self.required_features = artifact["requiredFeatures"]
        self.feature_importance = artifact.get("featureImportance", {})

    def explain_condition(self, condition: str) -> RootCauseDriverEvidence:
        """
        Return ML driver evidence for a condition.

        This is explainable because it is based on model feature importance.
        """

        if self.pipeline is None or not self.feature_importance:
            return RootCauseDriverEvidence(
                condition=condition,
                mlDriverScore=0.0,
                confidence="LOW",
                explanation="ML root cause model unavailable. Used Phase 1 logic only.",
                modelVersion=None,
                warnings=["Root cause driver model unavailable."],
            )

        condition_score = self.feature_importance.get("condition", 0.0)
        category_score = self.feature_importance.get("category", 0.0)
        amount_score = self.feature_importance.get("amount", 0.0)

        score = round(condition_score + category_score + amount_score, 4)

        confidence = "HIGH" if score >= 0.25 else "MEDIUM" if score >= 0.1 else "LOW"

        return RootCauseDriverEvidence(
            condition=condition,
            mlDriverScore=score,
            confidence=confidence,
            explanation=(
                f"{condition} is supported by ML driver evidence. "
                f"Important model drivers include condition, category, and amount."
            ),
            modelVersion=self.model_version,
            warnings=[],
        )