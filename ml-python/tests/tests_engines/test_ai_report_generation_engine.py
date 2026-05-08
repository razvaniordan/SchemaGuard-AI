from core.engines.ai_report_generation_engine import AIReportGenerationEngine
from models.analysis_models import (
    AIReportRequest,
    AIReportTransactionInput,
    RuleEngineResult,
)


def test_generates_ai_report():
    engine = AIReportGenerationEngine()

    current = RuleEngineResult(
        category="Ecom Non-Secure Credit",
        feeRate=1.85,
        feeAmount=9.25,
        transaction={
            "transactionId": "report-1",
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
            "transactionId": "report-1",
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

    request = AIReportRequest(
        reportName="Test AI Optimization Report",
        transactions=[
            AIReportTransactionInput(
                currentResult=current,
                optimalResult=optimal,
            )
        ],
    )

    response = engine.generate_report(request)

    assert response.reportId is not None
    assert response.summary.totalTransactions == 1
    assert response.summary.estimatedSavings == 3.0
    assert len(response.recommendationSummary) > 0
    assert response.summary.topRecommendation is not None