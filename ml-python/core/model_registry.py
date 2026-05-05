from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
from pydantic import BaseModel


class ModelMetadata(BaseModel):
    # Unique logical model name, for example "impact_prediction"
    name: str

    # Version identifier, for example "impact-model-v1"
    version: str

    # Date when the model was trained
    trainedDate: str

    # Required input fields for this model
    featureSchema: List[str]

    # Offline evaluation metrics
    metrics: Dict[str, Any]

    # File path to the saved model artifact
    artifactPath: str


class LoadedModelResult(BaseModel):
    # Whether the model was successfully loaded
    loaded: bool

    # Loaded model object, if available
    model: Optional[Any] = None

    # Metadata for the model version
    metadata: Optional[ModelMetadata] = None

    # Warning messages for fallback behavior
    warnings: List[str] = []

    class Config:
        arbitrary_types_allowed = True


class ModelRegistry:
    def __init__(self, registry: Optional[Dict[str, ModelMetadata]] = None) -> None:
        # In-memory registry, testable without database or external services
        self.registry = registry or {}

    def register_model(self, metadata: ModelMetadata) -> None:
        # Store model metadata by version
        self.registry[metadata.version] = metadata

    def get_metadata(self, version: str) -> Optional[ModelMetadata]:
        # Return model metadata if the version exists
        return self.registry.get(version)

    def load_model(
        self,
        version: str,
        available_features: Optional[List[str]] = None,
    ) -> LoadedModelResult:
        metadata = self.get_metadata(version)

        if metadata is None:
            return LoadedModelResult(
                loaded=False,
                warnings=[f"Unsupported model version '{version}'. Falling back to heuristic."],
            )

        if available_features is not None:
            missing_features = [
                feature
                for feature in metadata.featureSchema
                if feature not in available_features
            ]

            if missing_features:
                return LoadedModelResult(
                    loaded=False,
                    metadata=metadata,
                    warnings=[
                        f"Feature schema mismatch. Missing features: {missing_features}. Falling back to heuristic."
                    ],
                )

        artifact_path = Path(metadata.artifactPath)

        if not artifact_path.exists():
            return LoadedModelResult(
                loaded=False,
                metadata=metadata,
                warnings=[
                    f"Model artifact not found at '{metadata.artifactPath}'. Falling back to heuristic."
                ],
            )

        model = joblib.load(artifact_path)

        return LoadedModelResult(
            loaded=True,
            model=model,
            metadata=metadata,
            warnings=[],
        )