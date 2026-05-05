from core.missed_condition_detector import MissedConditionDetector
from models.analysis_models import RuleEngineResult


def test_detects_3ds_and_clearing_time():
    detector = MissedConditionDetector()

    current_result = RuleEngineResult(
        category="Ecom Non-Secure Credit",
        feeRate=1.85,
        feeAmount=9.25,
        transaction={
            "amount": 500,
            "currency": "RON",
            "country": "RO",
            "cardType": "Credit",
            "channel": "eCommerce",
            "mcc": "5732",
            "threeDS": False,
            "authDate": "2026-05-01",
            "clearingDate": "2026-05-03",
            "cardBrand": "Visa",
            "cardPresence": "CNP",
            "transactionType": "Purchase",
        },
    )

    optimal_result = RuleEngineResult(
        category="Ecom Secure Preferred Credit",
        feeRate=1.25,
        feeAmount=6.25,
        transaction={
            "amount": 500,
            "currency": "RON",
            "country": "RO",
            "cardType": "Credit",
            "channel": "eCommerce",
            "mcc": "5732",
            "threeDS": True,
            "authDate": "2026-05-01",
            "clearingDate": "2026-05-02",
            "cardBrand": "Visa",
            "cardPresence": "CNP",
            "transactionType": "Purchase",
        },
    )

    result = detector.analyze(current_result, optimal_result)

    conditions = [item.condition for item in result.missedConditions]

    assert "3DS authentication" in conditions
    assert "clearing time" in conditions
    assert result.currentCategory == "Ecom Non-Secure Credit"
    assert result.optimalCategory == "Ecom Secure Preferred Credit"
    assert len(result.missedConditions) == 2