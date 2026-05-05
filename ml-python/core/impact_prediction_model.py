from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import pandas as pd
from pydantic import BaseModel
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error


class ImpactPredictionResult(BaseModel):
    # Predicted financial impact for a missed condition
    predictedImpact: float

    # Confidence score between 0 and 1
    modelConfidence: float

    # Active model version
    modelVersion: Optional[str] = None

    # True when heuristic fallback was used
    fallbackUsed: bool = False

    # Warning messages for missing model, missing fields, or low confidence
    warnings: List[str] = []


class ImpactPredictionModel:
    def __init__(
        self,
        model_version: str = "impact-model-v1",
        confidence_threshold: float = 0.65,
        min_training_records: int = 20,
        random_state: int = 42,
    ) -> None:
        self.model_version = model_version
        self.confidence_threshold = confidence_threshold
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
            "condition",
            "paymentChannel",
            "threeDS",
            "mcc",
        ]

        self.required_features = self.numeric_features + self.categorical_features

    def train(self, training_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Train supervised model using historical ML records.

        Expected label column:
        - label_actualSavings

        This represents the real observed savings or financial impact.
        """

        if len(training_df) < self.min_training_records:
            return {
                "trained": False,
                "warnings": [
                    f"Small dataset. Need at least {self.min_training_records} records."
                ],
            }

        if "label_actualSavings" not in training_df.columns:
            return {
                "trained": False,
                "warnings": ["Missing label_actualSavings column."],
            }

        df = training_df.copy()

        # Keep only rows with labels
        df = df.dropna(subset=["label_actualSavings"])

        if len(df) < self.min_training_records:
            return {
                "trained": False,
                "warnings": ["Not enough labeled records after removing empty labels."],
            }

        for feature in self.required_features:
            if feature not in df.columns:
                df[feature] = None

        X = self._prepare_features(df)
        y = df["label_actualSavings"]

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

        model = RandomForestRegressor(
            n_estimators=100,
            random_state=self.random_state,
        )

        self.pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", model),
            ]
        )

        self.pipeline.fit(X, y)

        predictions = self.pipeline.predict(X)
        mae = float(mean_absolute_error(y, predictions))

        return {
            "trained": True,
            "modelVersion": self.model_version,
            "metrics": {
                "mae": round(mae, 4),
                "trainingRows": len(df),
            },
            "warnings": [],
        }

    def save(self, artifact_path: str) -> None:
        """
        Save trained model artifact.
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
        Load trained model artifact.
        """

        artifact = joblib.load(artifact_path)

        self.model_version = artifact["modelVersion"]
        self.pipeline = artifact["pipeline"]
        self.required_features = artifact["requiredFeatures"]

    def predict(
        self,
        features: Dict[str, Any],
        heuristic_impact: float,
    ) -> ImpactPredictionResult:
        """
        Predict impact using trained model.

        Falls back to heuristic when:
        - model is missing
        - required fields are missing
        - confidence is below threshold
        """

        warnings = []

        if self.pipeline is None:
            return ImpactPredictionResult(
                predictedImpact=heuristic_impact,
                modelConfidence=0.0,
                modelVersion=None,
                fallbackUsed=True,
                warnings=["Impact model unavailable. Falling back to heuristic."],
            )

        missing_features = [
            feature
            for feature in self.required_features
            if feature not in features
        ]

        if missing_features:
            return ImpactPredictionResult(
                predictedImpact=heuristic_impact,
                modelConfidence=0.0,
                modelVersion=self.model_version,
                fallbackUsed=True,
                warnings=[
                    f"Missing required features: {missing_features}. Falling back to heuristic."
                ],
            )

        input_df = self._prepare_features(pd.DataFrame([features]))

        predicted = float(self.pipeline.predict(input_df)[0])

        # Phase 2 confidence proxy:
        # Later this can be replaced with prediction interval or calibration.
        confidence = 0.85

        if confidence < self.confidence_threshold:
            warnings.append("Model confidence below threshold. Falling back to heuristic.")

            return ImpactPredictionResult(
                predictedImpact=heuristic_impact,
                modelConfidence=confidence,
                modelVersion=self.model_version,
                fallbackUsed=True,
                warnings=warnings,
            )

        return ImpactPredictionResult(
            predictedImpact=round(max(predicted, 0.0), 4),
            modelConfidence=confidence,
            modelVersion=self.model_version,
            fallbackUsed=False,
            warnings=[],
        )

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare numeric and categorical columns safely before training/prediction.
        """

        prepared = df.copy()

        for feature in self.required_features:
            if feature not in prepared.columns:
                prepared[feature] = None

        for feature in self.categorical_features:
            prepared[feature] = (
                prepared[feature]
                .fillna("UNKNOWN")
                .astype(str)
            )

        return prepared[self.required_features]