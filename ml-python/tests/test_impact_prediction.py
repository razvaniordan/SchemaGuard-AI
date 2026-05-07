import pandas as pd

from core.impact_prediction_model import ImpactPredictionModel


def test_small_dataset_uses_training_fallback():
    model = ImpactPredictionModel(min_training_records=20)

    df = pd.DataFrame(
        [
            {
                "amount": 100,
                "feeRate": 0.03,
                "feeAmount": 3,
                "clearingDelayDays": 2,
                "category": "standard",
                "condition": "3DS authentication",
                "paymentChannel": "card",
                "threeDS": False,
                "mcc": "5411",
                "label_actualSavings": 1.5,
            }
        ]
    )

    result = model.train(df)

    assert result["trained"] is False
    assert "Small dataset" in result["warnings"][0]


def test_model_can_train_and_predict():
    rows = []

    for index in range(30):
        rows.append(
            {
                "amount": 100 + index,
                "feeRate": 0.03,
                "feeAmount": 3 + index * 0.1,
                "clearingDelayDays": 2,
                "category": "standard",
                "condition": "3DS authentication",
                "paymentChannel": "card",
                "threeDS": False,
                "mcc": "5411",
                "label_actualSavings": 1.5 + index * 0.1,
            }
        )

    df = pd.DataFrame(rows)

    model = ImpactPredictionModel(min_training_records=20)
    train_result = model.train(df)

    assert train_result["trained"] is True

    prediction = model.predict(
        features={
            "amount": 120,
            "feeRate": 0.03,
            "feeAmount": 4,
            "clearingDelayDays": 2,
            "category": "standard",
            "condition": "3DS authentication",
            "paymentChannel": "card",
            "threeDS": False,
            "mcc": "5411",
        },
        heuristic_impact=2.0,
    )

    assert prediction.fallbackUsed is False
    assert prediction.predictedImpact >= 0
    assert prediction.modelConfidence >= 0.65
    assert prediction.modelVersion == "impact-model-v1"


def test_missing_features_falls_back_to_heuristic():
    rows = []

    for index in range(30):
        rows.append(
            {
                "amount": 100 + index,
                "feeRate": 0.03,
                "feeAmount": 3,
                "clearingDelayDays": 2,
                "category": "standard",
                "condition": "3DS authentication",
                "paymentChannel": "card",
                "threeDS": False,
                "mcc": "5411",
                "label_actualSavings": 2.0,
            }
        )

    model = ImpactPredictionModel(min_training_records=20)
    model.train(pd.DataFrame(rows))

    prediction = model.predict(
        features={
            "amount": 100,
            "feeRate": 0.03,
        },
        heuristic_impact=2.5,
    )

    assert prediction.fallbackUsed is True
    assert prediction.predictedImpact == 2.5
    assert "Missing required features" in prediction.warnings[0]


def test_model_can_save_and_reload(tmp_path):
    rows = []

    for index in range(30):
        rows.append(
            {
                "amount": 100 + index,
                "feeRate": 0.03,
                "feeAmount": 3,
                "clearingDelayDays": 2,
                "category": "standard",
                "condition": "3DS authentication",
                "paymentChannel": "card",
                "threeDS": False,
                "mcc": "5411",
                "label_actualSavings": 2.0,
            }
        )

    artifact_path = tmp_path / "impact-model-v1.joblib"

    model = ImpactPredictionModel(min_training_records=20)
    model.train(pd.DataFrame(rows))
    model.save(str(artifact_path))

    reloaded_model = ImpactPredictionModel()
    reloaded_model.load(str(artifact_path))

    prediction = reloaded_model.predict(
        features={
            "amount": 110,
            "feeRate": 0.03,
            "feeAmount": 3,
            "clearingDelayDays": 2,
            "category": "standard",
            "condition": "3DS authentication",
            "paymentChannel": "card",
            "threeDS": False,
            "mcc": "5411",
        },
        heuristic_impact=2.0,
    )

    assert prediction.fallbackUsed is False
    assert prediction.modelVersion == "impact-model-v1"