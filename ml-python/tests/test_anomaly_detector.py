from core.ml_core import MLCore
from models.analysis_models import RuleEngineResult


def _ml_core_without_ml() -> MLCore:
    ml_core = MLCore()
    ml_core.config["models"]["anomaly_detection"]["enabled"] = False
    return ml_core


def test_detects_fee_outlier():
    ml_core = _ml_core_without_ml()

    results = [
        RuleEngineResult(
            category="Normal",
            feeRate=1.0,
            feeAmount=5.0,
            transaction={
                "transactionId": "tx-1",
                "amount": 500,
                "channel": "ECOMMERCE",
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
                "channel": "ECOMMERCE",
                "threeDS": True,
                "authDate": "2026-05-01",
                "clearingDate": "2026-05-02",
            },
        ),
    ]

    result = ml_core.detect_anomalies(results)
    anomaly_types = [item.anomalyType for item in result.anomalies]

    assert "FEE_OUTLIER" in anomaly_types


def test_detects_category_mismatch():
    ml_core = _ml_core_without_ml()

    results = [
        RuleEngineResult(
            category="Ecom Non-Secure Credit",
            feeRate=1.85,
            feeAmount=9.25,
            transaction={
                "transactionId": "tx-1",
                "amount": 500,
                "channel": "ECOMMERCE",
                "threeDS": True,
                "authDate": "2026-05-01",
                "clearingDate": "2026-05-02",
            },
        )
    ]

    result = ml_core.detect_anomalies(results)
    anomaly_types = [item.anomalyType for item in result.anomalies]

    assert "CATEGORY_MISMATCH" in anomaly_types


def test_detects_late_clearing_anomaly():
    ml_core = _ml_core_without_ml()

    results = [
        RuleEngineResult(
            category="Normal",
            feeRate=1.25,
            feeAmount=6.25,
            transaction={
                "transactionId": "tx-1",
                "amount": 500,
                "channel": "ECOMMERCE",
                "threeDS": True,
                "authDate": "2026-05-01",
                "clearingDate": "2026-05-06",
            },
        )
    ]

    result = ml_core.detect_anomalies(results)

    assert len(result.anomalies) == 1
    assert result.anomalies[0].anomalyType == "LATE_CLEARING"
    assert result.anomalies[0].severity == "HIGH"


def test_detects_missing_3ds_for_ecommerce():
    ml_core = _ml_core_without_ml()

    results = [
        RuleEngineResult(
            category="Ecom Non-Secure Credit",
            feeRate=1.85,
            feeAmount=9.25,
            transaction={
                "transactionId": "tx-2",
                "amount": 500,
                "channel": "ECOMMERCE",
                "threeDS": False,
                "authDate": "2026-05-01",
                "clearingDate": "2026-05-03",
            },
        )
    ]

    result = ml_core.detect_anomalies(results)
    anomalies_by_type = {item.anomalyType: item for item in result.anomalies}

    assert "MISSING_3DS" in anomalies_by_type
    assert anomalies_by_type["MISSING_3DS"].severity == "MEDIUM"


def test_demo_transactions_business_expected_anomalies():
    ml_core = _ml_core_without_ml()

    results = [
        RuleEngineResult(
            category="Ecom Secure Credit",
            feeRate=1.0,
            feeAmount=5.0,
            transaction={
                "transactionId": "1",
                "amount": 500,
                "channel": "ECOMMERCE",
                "threeDS": True,
                "authDate": "2026-05-01",
                "clearingDate": "2026-05-01",
                "clearingDelayDays": 0,
            },
        ),
        RuleEngineResult(
            category="Ecom Non-Secure Credit",
            feeRate=1.85,
            feeAmount=9.25,
            transaction={
                "transactionId": "2",
                "amount": 500,
                "channel": "ECOMMERCE",
                "threeDS": False,
                "authDate": "2026-05-01",
                "clearingDate": "2026-05-03",
                "clearingDelayDays": 2,
            },
        ),
        RuleEngineResult(
            category="POS Credit",
            feeRate=1.0,
            feeAmount=2.5,
            transaction={
                "transactionId": "3",
                "amount": 250,
                "channel": "POS",
                "threeDS": True,
                "authDate": "2026-05-01",
                "clearingDate": "2026-05-01",
                "clearingDelayDays": 0,
            },
        ),
        RuleEngineResult(
            category="Ecom Non-Secure Credit",
            feeRate=1.85,
            feeAmount=1849.98,
            transaction={
                "transactionId": "4",
                "amount": 99999,
                "channel": "ECOMMERCE",
                "threeDS": False,
                "authDate": "2026-05-01",
                "clearingDate": "2026-05-04",
                "clearingDelayDays": 3,
            },
        ),
        RuleEngineResult(
            category="Ecom Non-Secure Credit",
            feeRate=1.85,
            feeAmount=2.22,
            transaction={
                "transactionId": "5",
                "amount": 120,
                "channel": "ECOMMERCE",
                "threeDS": False,
                "authDate": "2026-05-01",
                "clearingDate": "2026-05-03",
                "clearingDelayDays": 2,
            },
        ),
    ]

    result = ml_core.detect_anomalies(results)
    anomaly_keys = {(item.transactionId, item.anomalyType) for item in result.anomalies}

    assert ("1", "MISSING_3DS") not in anomaly_keys
    assert ("1", "LATE_CLEARING") not in anomaly_keys
    assert ("3", "MISSING_3DS") not in anomaly_keys
    assert ("3", "LATE_CLEARING") not in anomaly_keys

    assert ("2", "MISSING_3DS") in anomaly_keys
    assert ("2", "LATE_CLEARING") in anomaly_keys
    assert ("4", "MISSING_3DS") in anomaly_keys
    assert ("4", "LATE_CLEARING") in anomaly_keys
    assert ("5", "MISSING_3DS") in anomaly_keys
    assert ("5", "LATE_CLEARING") in anomaly_keys

    tx4_anomalies = [item for item in result.anomalies if item.transactionId == "4"]
    assert any(item.severity == "HIGH" for item in tx4_anomalies)


def test_missing_fields_return_warnings():
    ml_core = _ml_core_without_ml()

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

    result = ml_core.detect_anomalies(results)

    assert len(result.warnings) > 0
