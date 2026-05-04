from core.ml_core import MLCore
from models.analysis_models import RuleEngineResult


def test_ml_core_runs_full_pipeline():
    # Create ML core orchestrator
    ml_core = MLCore()

    # Current bad result
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

    # Optimal mock result
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

    # Run full ML pipeline
    result = ml_core.analyze_transaction(current_result, optimal_result)

    # It should detect two missed conditions
    assert len(result.analysis.missedConditions) == 2

    # It should generate ranked suggestions
    assert len(result.rankedSuggestions) == 2

    # It should apply suggestions in the simulated transaction
    assert result.simulation.simulatedTransaction["threeDS"] is True
    assert result.simulation.simulatedTransaction["clearingDate"] == "2026-05-02"

    # It should detect patterns
    assert result.detectedPatterns["mostCommonCondition"] is not None

    # It should select an algorithm
    assert result.algorithmUsed in {"heuristic", "decision_tree"}