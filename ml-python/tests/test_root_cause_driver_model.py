import pandas as pd

from core.root_cause_driver_model import RootCauseDriverModel


def test_low_data_volume_fallback():
    model = RootCauseDriverModel(min_training_records=100)

    df = pd.DataFrame(
        [
            {
                "amount": 100,
                "feeRate": 1.25,
                "feeAmount": 1.25,
                "clearingDelayDays": 1,
                "expectedImpact": 2.0,
                "historicalSuccessRate": 0.8,
                "category": "standard",
                "condition": "3DS authentication",
                "paymentChannel": "eCommerce",
                "threeDS": True,
                "mcc": "5732",
                "suggestionType": "ENABLE_3DS",
                "difficulty": "LOW",
                "label_actualSavings": 2.0,
            }
        ]
    )

    result = model.train(df)

    assert result["trained"] is False
    assert "Low data volume" in result["warnings"][0]


def test_no_high_loss_examples_returns_warning():
    rows = []

    for index in range(120):
        rows.append(
            {
                "amount": 100 + index,
                "feeRate": 1.25,
                "feeAmount": 1.25,
                "clearingDelayDays": 1,
                "expectedImpact": 1.0,
                "historicalSuccessRate": 0.8,
                "category": "standard",
                "condition": "3DS authentication",
                "paymentChannel": "eCommerce",
                "threeDS": True,
                "mcc": "5732",
                "suggestionType": "ENABLE_3DS",
                "difficulty": "LOW",
                "label_actualSavings": 1.0,
            }
        )

    model = RootCauseDriverModel(min_training_records=100, high_loss_threshold=5.0)
    result = model.train(pd.DataFrame(rows))

    assert result["trained"] is False
    assert "No high-loss examples" in result["warnings"][0]


def test_model_can_train_and_explain_driver():
    rows = []

    for index in range(120):
        rows.append(
            {
                "amount": 5000 + index,
                "feeRate": 1.85,
                "feeAmount": 90,
                "clearingDelayDays": 4,
                "expectedImpact": 8.0,
                "historicalSuccessRate": 0.8,
                "category": "Ecom Non-Secure Credit",
                "condition": "3DS authentication",
                "paymentChannel": "eCommerce",
                "threeDS": False,
                "mcc": "5732",
                "suggestionType": "ENABLE_3DS",
                "difficulty": "LOW",
                "label_actualSavings": 8.0,
            }
        )

    for index in range(120):
        rows.append(
            {
                "amount": 100 + index,
                "feeRate": 1.25,
                "feeAmount": 2,
                "clearingDelayDays": 1,
                "expectedImpact": 1.0,
                "historicalSuccessRate": 0.4,
                "category": "standard",
                "condition": "clearing time",
                "paymentChannel": "eCommerce",
                "threeDS": True,
                "mcc": "5411",
                "suggestionType": "OPTIMIZE_CLEARING",
                "difficulty": "MEDIUM",
                "label_actualSavings": 1.0,
            }
        )

    model = RootCauseDriverModel(min_training_records=100, high_loss_threshold=5.0)
    result = model.train(pd.DataFrame(rows))

    assert result["trained"] is True

    evidence = model.explain_condition("3DS authentication")

    assert evidence.mlDriverScore >= 0
    assert evidence.confidence in {"LOW", "MEDIUM", "HIGH"}
    assert "ML driver evidence" in evidence.explanation


def test_model_can_save_and_reload(tmp_path):
    rows = []

    for index in range(120):
        rows.append(
            {
                "amount": 5000 + index,
                "feeRate": 1.85,
                "feeAmount": 90,
                "clearingDelayDays": 4,
                "expectedImpact": 8.0,
                "historicalSuccessRate": 0.8,
                "category": "Ecom Non-Secure Credit",
                "condition": "3DS authentication",
                "paymentChannel": "eCommerce",
                "threeDS": False,
                "mcc": "5732",
                "suggestionType": "ENABLE_3DS",
                "difficulty": "LOW",
                "label_actualSavings": 8.0,
            }
        )

    for index in range(120):
        rows.append(
            {
                "amount": 100 + index,
                "feeRate": 1.25,
                "feeAmount": 2,
                "clearingDelayDays": 1,
                "expectedImpact": 1.0,
                "historicalSuccessRate": 0.4,
                "category": "standard",
                "condition": "clearing time",
                "paymentChannel": "eCommerce",
                "threeDS": True,
                "mcc": "5411",
                "suggestionType": "OPTIMIZE_CLEARING",
                "difficulty": "MEDIUM",
                "label_actualSavings": 1.0,
            }
        )

    artifact_path = tmp_path / "root-cause-model-v1.joblib"

    model = RootCauseDriverModel(min_training_records=100, high_loss_threshold=5.0)
    model.train(pd.DataFrame(rows))
    model.save(str(artifact_path))

    reloaded = RootCauseDriverModel()
    reloaded.load(str(artifact_path))

    evidence = reloaded.explain_condition("3DS authentication")

    assert reloaded.pipeline is not None
    assert evidence.modelVersion == "root-cause-model-v1"