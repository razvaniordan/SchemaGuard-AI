from core.engines.fee_comparison_engine import FeeComparisonEngine
from models.analysis_models import FeeComparisonRequest, RuleEngineResult


def test_fee_comparison_engine_returns_savings_and_predictions():
    engine = FeeComparisonEngine()

    current = RuleEngineResult(
        category="Ecom Non-Secure Credit",
        feeRate=1.85,
        feeAmount=9.25,
        transaction={
            "transactionId": "fee-compare-1",
            "amount": 5000,
            "paymentChannel": "eCommerce",
            "channel": "eCommerce",
            "mcc": "5732",
            "threeDS": False,
            "clearingDelayDays": 4,
            "authDate": "2026-05-01",
            "clearingDate": "2026-05-05",
        },
    )

    optimal = RuleEngineResult(
        category="Ecom Secure Preferred Credit",
        feeRate=1.25,
        feeAmount=6.25,
        transaction={
            "transactionId": "fee-compare-1",
            "amount": 5000,
            "paymentChannel": "eCommerce",
            "channel": "eCommerce",
            "mcc": "5732",
            "threeDS": True,
            "clearingDelayDays": 1,
            "authDate": "2026-05-01",
            "clearingDate": "2026-05-02",
        },
    )

    request = FeeComparisonRequest(
        currentResult=current,
        optimalResult=optimal,
        monthlyTransactionVolume=1000,
        yearlyTransactionVolume=12000,
        currency="RON",
    )

    response = engine.compare_fees(request)

    assert response.currentFeeAmount == 9.25
    assert response.optimizedFeeAmount == 6.25
    assert response.absoluteSavings == 3.0
    assert response.percentageSavings == 32.4324
    assert response.mlPredictedSavings >= 0
    assert response.mlConfidence >= 0
    assert response.predictionSource in {"ml_model", "heuristic"}
    assert response.monthlyProjectedSavings is not None
    assert response.yearlyProjectedSavings is not None
    assert response.absoluteSavingsEur == 0.6