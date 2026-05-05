from datetime import datetime

from models.analysis_models import HistoricalMLRecord
from core.historical_data_store import HistoricalDataStore


def test_store_valid_record():
    store = HistoricalDataStore()

    record = HistoricalMLRecord(
        transactionId="txn-1",
        timestamp=datetime.utcnow(),
        features={"amount": 100},
        labels={"actualSavings": 5},
        currentRuleEngineResult={},
        optimalRuleEngineResult={},
        missedConditions=[],
        rankedSuggestions=[],
        simulatedSavings=5,
        actualOutcome={"actualSavings": 5},
        modelVersion="v1",
        algorithmUsed="heuristic",
    )

    result = store.store(record)

    assert result.stored is True
    assert result.transactionId == "txn-1"
    assert len(store.get_all()) == 1

def test_store_missing_labels_as_unlabeled():
    store = HistoricalDataStore()

    record = HistoricalMLRecord(
        transactionId="txn-1",
        timestamp=datetime.utcnow(),
        features={"amount": 100},
        labels=None,
        currentRuleEngineResult={},
        optimalRuleEngineResult={},
        missedConditions=[],
        rankedSuggestions=[],
        simulatedSavings=None,
        actualOutcome=None,
        modelVersion=None,
        algorithmUsed="heuristic",
    )

    result = store.store(record)

    assert result.stored is True
    assert "Missing labels" in result.warnings[0]

def test_duplicate_transaction_update():
    store = HistoricalDataStore(duplicate_strategy="update")

    first = HistoricalMLRecord(
        transactionId="txn-1",
        timestamp=datetime.utcnow(),
        features={"amount": 100},
        labels=None,
        currentRuleEngineResult={},
        optimalRuleEngineResult={},
        missedConditions=[],
        rankedSuggestions=[],
        algorithmUsed="heuristic",
    )

    second = HistoricalMLRecord(
        transactionId="txn-1",
        timestamp=datetime.utcnow(),
        features={"amount": 200},
        labels=None,
        currentRuleEngineResult={},
        optimalRuleEngineResult={},
        missedConditions=[],
        rankedSuggestions=[],
        algorithmUsed="heuristic",
    )

    store.store(first)
    result = store.store(second)

    assert result.stored is True
    assert store.records["txn-1"].features["amount"] == 200

def test_export_to_dataframe():
    store = HistoricalDataStore()

    record = HistoricalMLRecord(
        transactionId="txn-1",
        timestamp=datetime.utcnow(),
        features={"amount": 100, "feeRate": 0.02},
        labels={"actualSavings": 5},
        currentRuleEngineResult={},
        optimalRuleEngineResult={},
        missedConditions=[],
        rankedSuggestions=[],
        algorithmUsed="heuristic",
    )

    store.store(record)

    df = store.to_dataframe()

    assert len(df) == 1
    assert df.iloc[0]["amount"] == 100
    assert df.iloc[0]["label_actualSavings"] == 5