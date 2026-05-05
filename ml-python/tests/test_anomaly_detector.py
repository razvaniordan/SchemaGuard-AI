from core.ml_core import MLCore
from models.analysis_models import RuleEngineResult


def test_detects_fee_outlier():
    # Create ML core instance
    ml_core = MLCore()

    # Only two transactions means fallback threshold is used
    results = [
        RuleEngineResult(
            category="Normal",
            feeRate=1.0,
            feeAmount=5.0,
            transaction={
                "transactionId": "tx-1",
                "amount": 500,
                "threeDS": True,
                "authDate": "2026-05-01",
                "clearingDate": "2026-05-02",
            },
        ),
        RuleEngineResult(
            category="Normal",
            feeRate=2.5,
            feeAmount=12.5,
            transaction={
                "transactionId": "tx-2",
                "amount": 500,
                "threeDS": True,
                "authDate": "2026-05-01",
                "clearingDate": "2026-05-02",
            },
        ),
    ]

    # Run anomaly detection
    result = ml_core.detect_anomalies(results)

    # Validate fallback rule catches high fee
    anomaly_types = [item.anomalyType for item in result.anomalies]

    assert "FEE_OUTLIER" in anomaly_types


def test_detects_category_mismatch():
    # Create ML core instance
    ml_core = MLCore()

    # 3DS is enabled but category says non-secure
    results = [
        RuleEngineResult(
            category="Ecom Non-Secure Credit",
            feeRate=1.85,
            feeAmount=9.25,
            transaction={
                "transactionId": "tx-1",
                "amount": 500,
                "threeDS": True,
                "authDate": "2026-05-01",
                "clearingDate": "2026-05-02",
            },
        )
    ]

    # Run anomaly detection
    result = ml_core.detect_anomalies(results)

    # Validate category mismatch was found
    assert len(result.anomalies) == 1
    assert result.anomalies[0].anomalyType == "CATEGORY_MISMATCH"


def test_detects_timing_anomaly():
    # Create ML core instance
    ml_core = MLCore()

    # Clearing happens 5 days after authorization
    results = [
        RuleEngineResult(
            category="Normal",
            feeRate=1.25,
            feeAmount=6.25,
            transaction={
                "transactionId": "tx-1",
                "amount": 500,
                "threeDS": True,
                "authDate": "2026-05-01",
                "clearingDate": "2026-05-06",
            },
        )
    ]

    # Run anomaly detection
    result = ml_core.detect_anomalies(results)

    # Validate timing anomaly was found
    assert len(result.anomalies) == 1
    assert result.anomalies[0].anomalyType == "TIMING_ANOMALY"
    assert result.anomalies[0].severity == "HIGH"


def test_missing_fields_return_warnings():
    # Create ML core instance
    ml_core = MLCore()

    # Missing threeDS, authDate, and clearingDate
    results = [
        RuleEngineResult(
            category="Normal",
            feeRate=1.25,
            feeAmount=6.25,
            transaction={
                "transactionId": "tx-1",
                "amount": 500,
            },
        )
    ]

    # Run anomaly detection
    result = ml_core.detect_anomalies(results)

    # Validate warning messages were returned
    assert len(result.warnings) > 0