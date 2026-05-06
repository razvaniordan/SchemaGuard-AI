from core.ml_core import MLCore
from models.analysis_models import RuleEngineResult
from core.model_registry import ModelMetadata, ModelRegistry

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
    assert result.algorithmUsed in {
        "heuristic+heuristic_ranking",
        "decision_tree+heuristic_ranking",
        "heuristic+ml_ranking",
        "decision_tree+ml_ranking",
    }

def test_analyze_transaction_can_persist_history():
    ml_core = MLCore()

    current = RuleEngineResult(
        category="standard",
        feeRate=0.03,
        feeAmount=3.0,
        transaction={
            "transactionId": "txn-history-1",
            "amount": 100,
            "threeDS": False,
            "clearingDelayDays": 3,
        },
    )

    optimal = RuleEngineResult(
        category="optimized",
        feeRate=0.01,
        feeAmount=1.0,
        transaction={
            "transactionId": "txn-history-1",
            "amount": 100,
            "threeDS": True,
            "clearingDelayDays": 1,
        },
    )

    response = ml_core.analyze_transaction(
        current,
        optimal,
        persist_history=True,
        actual_outcome={"actualFeeAmount": 1.2, "actualSavings": 1.8},
    )

    records = ml_core._historical_store.get_all()

    assert response.algorithmUsed is not None
    assert len(records) == 1
    assert records[0].transactionId == "txn-history-1"
    assert records[0].labels["actualSavings"] == 1.8

def test_ml_core_load_active_model_falls_back_when_artifact_missing():
    ml_core = MLCore()

    result = ml_core.load_active_model(
        model_key="impact_prediction",
        available_features=[
            "amount",
            "feeRate",
            "feeAmount",
            "category",
            "threeDS",
            "clearingDelayDays",
        ],
    )

    assert result.loaded is False
    assert result.metadata.version == "impact-model-v1"
    assert "Model artifact not found" in result.warnings[0]

def test_ml_core_load_active_model_falls_back_when_artifact_missing():
    ml_core = MLCore()

    registry = ModelRegistry()
    registry.register_model(
        ModelMetadata(
            name="impact_prediction",
            version="impact-model-v1",
            trainedDate="2026-05-05",
            featureSchema=[
                "amount",
                "feeRate",
                "feeAmount",
                "category",
                "threeDS",
                "clearingDelayDays",
            ],
            metrics={},
            artifactPath="missing/path/impact-model-v1.joblib",
        )
    )

    ml_core._model_registry = registry

    result = ml_core.load_active_model(
        model_key="impact_prediction",
        available_features=[
            "amount",
            "feeRate",
            "feeAmount",
            "category",
            "threeDS",
            "clearingDelayDays",
        ],
    )

    assert result.loaded is False
    assert "Model artifact not found" in result.warnings[0]

def test_select_ranking_algorithm_uses_heuristic_for_small_transaction():
    ml_core = MLCore()

    current = RuleEngineResult(
        category="standard",
        feeRate=0.03,
        feeAmount=3.0,
        transaction={"transactionId": "txn-small", "amount": 100},
    )

    result = ml_core._select_ranking_algorithm(current)

    assert result == "heuristic_ranking"


def test_select_ranking_algorithm_uses_ml_for_large_transaction():
    ml_core = MLCore()

    current = RuleEngineResult(
        category="standard",
        feeRate=0.03,
        feeAmount=30.0,
        transaction={"transactionId": "txn-large", "amount": 1500},
    )

    result = ml_core._select_ranking_algorithm(current)

    assert result == "ml_ranking"