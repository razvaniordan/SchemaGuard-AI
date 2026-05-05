from core.ml_core import MLCore
from models.analysis_models import RuleEngineResult

ml_core = MLCore()

current = RuleEngineResult(
    category="standard",
    feeRate=0.03,
    feeAmount=3.0,
    transaction={
        "transactionId": "manual-txn-1",
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
        "transactionId": "manual-txn-1",
        "amount": 100,
        "threeDS": True,
        "clearingDelayDays": 1,
    },
)

response = ml_core.analyze_transaction(
    current,
    optimal,
    persist_history=True,
    actual_outcome={
        "actualFeeAmount": 1.2,
        "actualSavings": 1.8,
        "successfulRecommendation": True,
    },
)

records = ml_core._historical_store.get_all()
df = ml_core._historical_store.to_dataframe()

print("Algorithm used:", response.algorithmUsed)
print("Stored records:", len(records))
print("First transaction ID:", records[0].transactionId)
print("Labels:", records[0].labels)
print(df.head())