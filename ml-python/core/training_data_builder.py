from datetime import datetime
from typing import Any, Dict, Optional
from core.transaction_schema import normalize_transaction, get_payment_channel
from models.analysis_models import (
    HistoricalMLRecord,
    RuleEngineResult,
    MLCoreResponse,
)


class TrainingDataBuilder:
    def build_record(
        self,
        current_result: RuleEngineResult,
        optimal_result: RuleEngineResult,
        ml_response: MLCoreResponse,
        actual_outcome: Optional[Dict[str, Any]] = None,
        model_version: Optional[str] = None,
    ) -> HistoricalMLRecord:
        transaction = current_result.transaction
        transaction = normalize_transaction(transaction)
        transaction_id = transaction.get("transactionId") or transaction.get("id")

        features = {
            "transactionId": transaction_id,
            "amount": transaction.get("amount"),
            "currency": transaction.get("currency"),
            "merchantCountry": transaction.get("merchantCountry"),
            "issuerCountry": transaction.get("issuerCountry"),
            "region": transaction.get("region"),
            "cardType": transaction.get("cardType"),
            "cardBrand": transaction.get("cardBrand"),
            "cardPresence": transaction.get("cardPresence"),
            "channel": transaction.get("channel"),
            "paymentChannel": get_payment_channel(transaction),
            "mcc": transaction.get("mcc"),
            "threeDS": transaction.get("threeDS"),
            "eci": transaction.get("eci"),
            "authDate": transaction.get("authDate"),
            "clearingDate": transaction.get("clearingDate"),
            "clearingDelayDays": transaction.get("clearingDelayDays"),
            "category": current_result.category,
            "feeRate": current_result.feeRate,
            "feeAmount": current_result.feeAmount,
            "optimalCategory": optimal_result.category,
            "optimalFeeRate": optimal_result.feeRate,
            "optimalFeeAmount": optimal_result.feeAmount,
        }

        labels = None

        if actual_outcome:
            labels = {
                "actualFeeAmount": actual_outcome.get("actualFeeAmount"),
                "actualSavings": actual_outcome.get("actualSavings"),
                "successfulRecommendation": actual_outcome.get(
                    "successfulRecommendation"
                ),
            }

        simulated_savings = max(
            current_result.feeAmount - optimal_result.feeAmount,
            0,
        )

        return HistoricalMLRecord(
            transactionId=transaction_id,
            timestamp=datetime.utcnow(),
            features=features,
            labels=labels,
            currentRuleEngineResult=current_result.dict(),
            optimalRuleEngineResult=optimal_result.dict(),
            missedConditions=[
                item.dict()
                for item in ml_response.analysis.missedConditions
            ],
            rankedSuggestions=[
                item.dict()
                for item in ml_response.rankedSuggestions
            ],
            simulatedSavings=simulated_savings,
            actualOutcome=actual_outcome,
            modelVersion=model_version,
            algorithmUsed=ml_response.algorithmUsed,
        )