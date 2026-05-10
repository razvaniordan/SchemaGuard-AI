from core.ml_core import MLCore
from models.analysis_models import FeeComparisonRequest, FeeComparisonResponse
from core.transaction_schema import normalize_transaction, get_payment_channel


class FeeComparisonEngine:
    def __init__(self) -> None:
        # Reuse MLCore because it already owns the impact prediction model and fallback logic.
        self.ml_core = MLCore()

        # Fixed demo exchange rate.
        # In production, this should come from an FX service or configuration.
        self.ron_to_eur_rate = 0.20

    def compare_fees(self, request: FeeComparisonRequest) -> FeeComparisonResponse:
        current = request.currentResult
        optimal = request.optimalResult
        current_transaction = normalize_transaction(current.transaction)

        # Deterministic fee comparison based on current and optimized rule-engine outputs.
        absolute_savings = round(max(current.feeAmount - optimal.feeAmount, 0.0), 4)

        # Avoid division by zero.
        if current.feeAmount > 0:
            percentage_savings = round((absolute_savings / current.feeAmount) * 100, 4)
        else:
            percentage_savings = 0.0

        # Build the feature payload expected by ImpactPredictionModel.
        features = {
            "amount": current_transaction.get("amount"),
            "feeRate": current.feeRate,
            "feeAmount": current.feeAmount,
            "clearingDelayDays": current_transaction.get("clearingDelayDays"),
            "category": current.category,
            "condition": self._infer_primary_condition(current, optimal),
            "paymentChannel": get_payment_channel(current_transaction),
            "threeDS": current_transaction.get("threeDS"),
            "mcc": current_transaction.get("mcc"),
        }

        # MLCore will use the trained impact model if available.
        # If the model is disabled or unavailable, it safely falls back to heuristic savings.
        prediction = self.ml_core.predict_impact(
            features=features,
            heuristic_impact=absolute_savings,
        )

        ml_predicted_savings = round(float(prediction["predictedImpact"]), 4)

        monthly_projection = self._project_savings(
            ml_predicted_savings,
            request.monthlyTransactionVolume,
        )

        yearly_projection = self._project_savings(
            ml_predicted_savings,
            request.yearlyTransactionVolume,
        )

        current_fee_eur = None
        optimized_fee_eur = None
        savings_eur = None

        # Convert RON values to EUR for demo/reporting purposes.
        if request.currency == "RON":
            current_fee_eur = self._ron_to_eur(current.feeAmount)
            optimized_fee_eur = self._ron_to_eur(optimal.feeAmount)
            savings_eur = self._ron_to_eur(absolute_savings)

        return FeeComparisonResponse(
            currentFeeAmount=round(current.feeAmount, 4),
            optimizedFeeAmount=round(optimal.feeAmount, 4),
            absoluteSavings=absolute_savings,
            percentageSavings=percentage_savings,
            mlPredictedSavings=ml_predicted_savings,
            mlConfidence=prediction["modelConfidence"],
            predictionSource="heuristic" if prediction["fallbackUsed"] else "ml_model",
            modelVersion=prediction["modelVersion"],
            fallbackUsed=prediction["fallbackUsed"],
            warnings=prediction["warnings"],
            monthlyProjectedSavings=monthly_projection,
            yearlyProjectedSavings=yearly_projection,
            currency=request.currency or "RON",
            currentFeeAmountEur=current_fee_eur,
            optimizedFeeAmountEur=optimized_fee_eur,
            absoluteSavingsEur=savings_eur,
        )

    def _infer_primary_condition(self, current, optimal) -> str:
        current_tx = normalize_transaction(current.transaction)
        optimal_tx = normalize_transaction(optimal.transaction)

        if current_tx.get("threeDS") != optimal_tx.get("threeDS"):
            return "3DS authentication"

        if current_tx.get("clearingDelayDays") != optimal_tx.get("clearingDelayDays"):
            return "clearing time"

        if current_tx.get("clearingDate") != optimal_tx.get("clearingDate"):
            return "clearing time"

        if current_tx.get("mcc") != optimal_tx.get("mcc"):
            return "MCC classification"

        if current_tx.get("channel") != optimal_tx.get("channel"):
            return "payment channel"

        return "UNKNOWN"

    def _project_savings(self, predicted_savings: float, volume: int | None) -> float | None:
        # Return no projection if no volume was provided.
        if volume is None:
            return None

        # Negative transaction volume should not produce negative projections.
        if volume < 0:
            return 0.0

        return round(predicted_savings * volume, 4)

    def _ron_to_eur(self, value: float) -> float:
        # Convert RON to EUR using a fixed MVP exchange rate.
        return round(value * self.ron_to_eur_rate, 4)