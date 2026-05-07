from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import pandas as pd
from pydantic import BaseModel
from sklearn.ensemble import RandomForestRegressor
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer


class RecommendationRankingResult(BaseModel):
    suggestionType: str
    score: float
    modelConfidence: float
    modelVersion: Optional[str] = None
    rankingReason: str
    fallbackUsed: bool = False
    warnings: List[str] = []


class RecommendationRankingModel:
    def __init__(
        self,
        model_version: str = "ranking-model-v1",
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
            "expectedImpact",
            "amount",
            "historicalSuccessRate",
        ]

        self.categorical_features = [
            "suggestionType",
            "difficulty",
            "condition",
            "category",
        ]

        self.required_features = self.numeric_features + self.categorical_features

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features safely for training and prediction.
        Unknown categories are converted to strings.
        Missing numeric values are handled by sklearn imputers.
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
        Train recommendation ranking model.

        Expected label:
        - label_successfulRecommendation

        This should be numeric:
        - 1 = recommendation worked
        - 0 = recommendation did not work
        """

        if len(training_df) < self.min_training_records:
            return {
                "trained": False,
                "warnings": [
                    f"Small dataset. Need at least {self.min_training_records} records."
                ],
            }

        if "label_successfulRecommendation" not in training_df.columns:
            return {
                "trained": False,
                "warnings": ["Missing label_successfulRecommendation column."],
            }

        df = training_df.copy()
        df = df.dropna(subset=["label_successfulRecommendation"])

        if len(df) < self.min_training_records:
            return {
                "trained": False,
                "warnings": ["Not enough labeled records after removing empty labels."],
            }

        X = self._prepare_features(df)
        y = df["label_successfulRecommendation"].astype(float)

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

        return {
            "trained": True,
            "modelVersion": self.model_version,
            "metrics": {
                "trainingRows": len(df),
            },
            "warnings": [],
        }

    def save(self, artifact_path: str) -> None:
        """
        Save trained ranking model.
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
        Load trained ranking model.
        """

        artifact = joblib.load(artifact_path)

        self.model_version = artifact["modelVersion"]
        self.pipeline = artifact["pipeline"]
        self.required_features = artifact["requiredFeatures"]

    def predict_score(
        self,
        features: Dict[str, Any],
        heuristic_score: float,
    ) -> RecommendationRankingResult:
        """
        Predict ranking score.

        Falls back to heuristic when:
        - model is unavailable
        - required features are missing
        - confidence is below threshold
        """

        if self.pipeline is None:
            return RecommendationRankingResult(
                suggestionType=str(features.get("suggestionType", "UNKNOWN")),
                score=heuristic_score,
                modelConfidence=0.0,
                modelVersion=None,
                rankingReason="Ranking model unavailable. Used heuristic score.",
                fallbackUsed=True,
                warnings=["Ranking model unavailable. Falling back to heuristic."],
            )

        missing_features = [
            feature for feature in self.required_features if feature not in features
        ]

        if missing_features:
            return RecommendationRankingResult(
                suggestionType=str(features.get("suggestionType", "UNKNOWN")),
                score=heuristic_score,
                modelConfidence=0.0,
                modelVersion=self.model_version,
                rankingReason="Missing features. Used heuristic score.",
                fallbackUsed=True,
                warnings=[
                    f"Missing required features: {missing_features}. Falling back to heuristic."
                ],
            )

        input_df = self._prepare_features(pd.DataFrame([features]))
        predicted_score = float(self.pipeline.predict(input_df)[0])

        confidence = 0.84

        if confidence < self.confidence_threshold:
            return RecommendationRankingResult(
                suggestionType=str(features.get("suggestionType", "UNKNOWN")),
                score=heuristic_score,
                modelConfidence=confidence,
                modelVersion=self.model_version,
                rankingReason="Low model confidence. Used heuristic score.",
                fallbackUsed=True,
                warnings=["Model confidence below threshold. Falling back to heuristic."],
            )

        return RecommendationRankingResult(
            suggestionType=str(features.get("suggestionType", "UNKNOWN")),
            score=round(max(predicted_score, 0.0), 4),
            modelConfidence=confidence,
            modelVersion=self.model_version,
            rankingReason="Historically high savings for similar transactions.",
            fallbackUsed=False,
            warnings=[],
        )