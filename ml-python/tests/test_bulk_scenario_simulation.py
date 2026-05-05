from core.ml_core import MLCore
from models.analysis_models import (
    BulkSimulationRequest,
    BulkSimulationTransactionInput,
    RuleEngineResult,
)


def test_bulk_simulation_calculates_total_savings():
    # Create ML core instance
    ml_core = MLCore()

    # Current transaction has higher fee than optimal transaction
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

    # Optimal transaction represents the better fee outcome
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

    request = BulkSimulationRequest(
        transactions=[
            BulkSimulationTransactionInput(
                currentResult=current_result,
                optimalResult=optimal_result,
            )
        ],
        applyTopNRecommendations=2,
    )

    # Run bulk simulation
    result = ml_core.simulate_bulk_scenarios(request)

    # Full possible saving is 9.25 - 6.25 = 3.00
    assert result.totalCurrentFees == 9.25
    assert result.totalSimulatedFees == 6.25
    assert result.totalSavings == 3.0

    # Transaction should be processed successfully
    assert result.processedTransactions == 1
    assert result.skippedTransactions == []

    # Savings should be grouped by recommendation type
    assert "ENABLE_3DS" in result.savingsByCondition
    assert "REDUCE_CLEARING_TIME" in result.savingsByCondition


def test_bulk_simulation_no_suggestions_means_zero_savings():
    # Create ML core instance
    ml_core = MLCore()

    # Current and optimal are identical, so no missed conditions should exist
    current_result = RuleEngineResult(
        category="Same Category",
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

    request = BulkSimulationRequest(
        transactions=[
            BulkSimulationTransactionInput(
                currentResult=current_result,
                optimalResult=current_result,
            )
        ],
        applyTopNRecommendations=2,
    )

    # Run bulk simulation
    result = ml_core.simulate_bulk_scenarios(request)

    assert result.totalCurrentFees == 6.25
    assert result.totalSimulatedFees == 6.25
    assert result.totalSavings == 0.0
    assert result.savingsByCondition == {}
    assert result.processedTransactions == 1


def test_bulk_simulation_excludes_invalid_simulated_transactions():
    # Create ML core instance
    ml_core = MLCore()

    # Current transaction can generate a clearingDate recommendation
    current_result = RuleEngineResult(
        category="Late Clearing",
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
            "authDate": "2026-05-05",
            "clearingDate": "2026-05-06",
            "cardBrand": "Visa",
            "cardPresence": "CNP",
            "transactionType": "Purchase",
        },
    )

    # Optimal clearing date is before auth date, which should fail simulator validation
    optimal_result = RuleEngineResult(
        category="Invalid Optimal",
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
            "authDate": "2026-05-05",
            "clearingDate": "2026-05-01",
            "cardBrand": "Visa",
            "cardPresence": "CNP",
            "transactionType": "Purchase",
        },
    )

    request = BulkSimulationRequest(
        transactions=[
            BulkSimulationTransactionInput(
                currentResult=current_result,
                optimalResult=optimal_result,
            )
        ],
        applyTopNRecommendations=2,
    )

    # Run bulk simulation
    result = ml_core.simulate_bulk_scenarios(request)

    assert result.processedTransactions == 0
    assert len(result.skippedTransactions) == 1
    assert "Clearing date cannot be before authorization date" in result.skippedTransactions[0].reason