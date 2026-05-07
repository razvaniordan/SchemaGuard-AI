import pandas as pd

from core.ml_anomaly_detection_model import MLAnomalyDetectionModel


def test_small_dataset_does_not_train():
    model = MLAnomalyDetectionModel(min_training_records=100)

    df = pd.DataFrame(
        [
            {
                "amount": 100,
                "feeRate": 1.25,
                "feeAmount": 1.25,
                "clearingDelayDays": 1,
                "category": "standard",
                "paymentChannel": "eCommerce",
                "threeDS": True,
                "mcc": "5732",
            }
        ]
    )

    result = model.train(df)

    assert result["trained"] is False
    assert "Small dataset" in result["warnings"][0]


def test_model_can_train_and_detect_anomaly():
    rows = []

    for index in range(200):
        rows.append(
            {
                "amount": 100 + index,
                "feeRate": 1.25,
                "feeAmount": 2.0,
                "clearingDelayDays": 1,
                "category": "Ecom Secure Preferred Credit",
                "paymentChannel": "eCommerce",
                "threeDS": True,
                "mcc": "5732",
            }
        )

    df = pd.DataFrame(rows)

    model = MLAnomalyDetectionModel(min_training_records=100, contamination=0.05)
    train_result = model.train(df)

    assert train_result["trained"] is True

    results = model.detect_batch(
        [
            {
                "transactionId": "anomaly-1",
                "amount": 9999,
                "feeRate": 5.0,
                "feeAmount": 500,
                "clearingDelayDays": 9,
                "category": "Ecom Secure Preferred Credit",
                "paymentChannel": "eCommerce",
                "threeDS": False,
                "mcc": "9999",
            }
        ]
    )

    assert len(results) >= 1
    assert results[0].transactionId == "anomaly-1"
    assert results[0].anomalyType == "ML_ANOMALY"


def test_missing_features_are_skipped():
    rows = []

    for index in range(200):
        rows.append(
            {
                "amount": 100 + index,
                "feeRate": 1.25,
                "feeAmount": 2.0,
                "clearingDelayDays": 1,
                "category": "standard",
                "paymentChannel": "eCommerce",
                "threeDS": True,
                "mcc": "5732",
            }
        )

    model = MLAnomalyDetectionModel(min_training_records=100)
    model.train(pd.DataFrame(rows))

    results = model.detect_batch(
        [
            {
                "transactionId": "bad-1",
                "amount": 100,
            }
        ]
    )

    assert results == []


def test_model_can_save_and_reload(tmp_path):
    rows = []

    for index in range(200):
        rows.append(
            {
                "amount": 100 + index,
                "feeRate": 1.25,
                "feeAmount": 2.0,
                "clearingDelayDays": 1,
                "category": "standard",
                "paymentChannel": "eCommerce",
                "threeDS": True,
                "mcc": "5732",
            }
        )

    artifact_path = tmp_path / "anomaly-model-v1.joblib"

    model = MLAnomalyDetectionModel(min_training_records=100)
    model.train(pd.DataFrame(rows))
    model.save(str(artifact_path))

    reloaded = MLAnomalyDetectionModel()
    reloaded.load(str(artifact_path))

    assert reloaded.pipeline is not None
    assert reloaded.model_version == "anomaly-model-v1"