from core.engines.ml_analytics_engine import MLAnalyticsEngine
from models.analysis_models import (
    MLAnalyticsRequest,
    MLAnalyticsTransactionInput,
    RuleEngineResult,
)


def test_generates_ml_portfolio_analytics():
    engine = MLAnalyticsEngine()

    current = RuleEngineResult(
        category="Ecom Non-Secure Credit",
        feeRate=1.85,
        feeAmount=9.25,
        transaction={
            "transactionId": "analytics-1",
            "amount": 5000,
            "currency": "RON",
            "country": "RO",
            "cardType": "Credit",
            "channel": "eCommerce",
            "paymentChannel": "eCommerce",
            "mcc": "5732",
            "threeDS": False,
            "authDate": "2026-05-01",
            "clearingDate": "2026-05-05",
            "clearingDelayDays": 4,
            "cardBrand": "Visa",
            "cardPresence": "CNP",
            "transactionType": "Purchase",
        },
    )

    optimal = RuleEngineResult(
        category="Ecom Secure Preferred Credit",
        feeRate=1.25,
        feeAmount=6.25,
        transaction={
            "transactionId": "analytics-1",
            "amount": 5000,
            "currency": "RON",
            "country": "RO",
            "cardType": "Credit",
            "channel": "eCommerce",
            "paymentChannel": "eCommerce",
            "mcc": "5732",
            "threeDS": True,
            "authDate": "2026-05-01",
            "clearingDate": "2026-05-02",
            "clearingDelayDays": 1,
            "cardBrand": "Visa",
            "cardPresence": "CNP",
            "transactionType": "Purchase",
        },
    )

    request = MLAnalyticsRequest(
        transactions=[
            MLAnalyticsTransactionInput(
                currentResult=current,
                optimalResult=optimal,
            )
        ]
    )

    response = engine.analyze_portfolio(request)

    assert response.totalTransactions == 1
    assert len(response.recommendationSuccessMetrics) > 0
    assert len(response.rootCauseDrivers) > 0
    assert len(response.transactionDrilldown) == 1
    assert response.transactionDrilldown[0].transactionId == "analytics-1"