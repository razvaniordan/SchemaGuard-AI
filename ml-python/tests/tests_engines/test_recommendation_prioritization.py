from core.engines.recommendation_prioritization_engine import RecommendationPrioritizationEngine
from models.analysis_models import RecommendationPrioritizationRequest, RuleEngineResult


def test_prioritizes_recommendations():
    engine = RecommendationPrioritizationEngine()

    current = RuleEngineResult(
        category="Ecom Non-Secure Credit",
        feeRate=1.85,
        feeAmount=9.25,
        transaction={
            "transactionId": "priority-1",
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
            "transactionId": "priority-1",
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

    request = RecommendationPrioritizationRequest(
        currentResult=current,
        optimalResult=optimal,
    )

    response = engine.prioritize(request)

    assert len(response.recommendations) == 2
    assert response.recommendations[0].score >= response.recommendations[1].score
    assert response.recommendations[0].priority in {"HIGH", "MEDIUM", "LOW"}
    assert response.algorithmUsed is not None