import joblib
from sklearn.tree import DecisionTreeClassifier

from core.model_registry import ModelMetadata, ModelRegistry


def test_successful_model_loading(tmp_path):
    artifact_path = tmp_path / "impact-model-v1.joblib"

    model = DecisionTreeClassifier()
    joblib.dump(model, artifact_path)

    registry = ModelRegistry()

    registry.register_model(
        ModelMetadata(
            name="impact_prediction",
            version="impact-model-v1",
            trainedDate="2026-05-05",
            featureSchema=["amount", "feeRate"],
            metrics={"mae": 1.2},
            artifactPath=str(artifact_path),
        )
    )

    result = registry.load_model(
        version="impact-model-v1",
        available_features=["amount", "feeRate"],
    )

    assert result.loaded is True
    assert result.model is not None
    assert result.metadata.version == "impact-model-v1"
    assert result.warnings == []


def test_missing_model_version_falls_back():
    registry = ModelRegistry()

    result = registry.load_model(
        version="unknown-model",
        available_features=["amount"],
    )

    assert result.loaded is False
    assert "Unsupported model version" in result.warnings[0]


def test_missing_artifact_falls_back():
    registry = ModelRegistry()

    registry.register_model(
        ModelMetadata(
            name="impact_prediction",
            version="impact-model-v1",
            trainedDate="2026-05-05",
            featureSchema=["amount"],
            metrics={},
            artifactPath="missing/path/model.joblib",
        )
    )

    result = registry.load_model(
        version="impact-model-v1",
        available_features=["amount"],
    )

    assert result.loaded is False
    assert "Model artifact not found" in result.warnings[0]


def test_feature_schema_mismatch_falls_back():
    registry = ModelRegistry()

    registry.register_model(
        ModelMetadata(
            name="impact_prediction",
            version="impact-model-v1",
            trainedDate="2026-05-05",
            featureSchema=["amount", "feeRate", "category"],
            metrics={},
            artifactPath="missing/path/model.joblib",
        )
    )

    result = registry.load_model(
        version="impact-model-v1",
        available_features=["amount", "feeRate"],
    )

    assert result.loaded is False
    assert "Feature schema mismatch" in result.warnings[0]