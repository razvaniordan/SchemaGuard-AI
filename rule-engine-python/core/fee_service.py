"""Fee calculation service adapter.

Links the existing FeeCalculator with classification and REST API contracts.
"""

from __future__ import annotations

import logging
from decimal import Decimal

from fee_calculator import FeeCalculator, FeeCap
from models import (
    ClassificationResult,
    FeeCalculationRequest,
    FeeCalculationResult,
    TransactionInput,
)

logger = logging.getLogger(__name__)


class FeeCalculationService:
    """Application-level fee calculation service."""

    def __init__(self, calculator: FeeCalculator | None = None) -> None:
        self.calculator = calculator or FeeCalculator()

    def calculate(self, request: FeeCalculationRequest) -> FeeCalculationResult:
        """Calculate fee from standalone REST request."""

        cap = None

        if request.cap is not None:
            cap = FeeCap(
                min_fee=request.cap.min_fee,
                max_fee=request.cap.max_fee,
            )

        result = self.calculator.calculate(
            amount=request.amount,
            fee_rate=request.fee_rate,
            currency=request.currency,
            cap=cap,
        )

        return self._to_api_result(result)

    def calculate_for_classification(
        self,
        *,
        transaction: TransactionInput,
        classification: ClassificationResult,
    ) -> FeeCalculationResult | None:
        """Calculate fee using transaction amount and classification fee rate.

        Returns None when amount is missing, because classification can still
        be valid without amount, but financial calculation cannot.
        """

        if transaction.amount is None:
            logger.info(
                "Skipping fee calculation because amount is missing transaction_id=%s",
                transaction.transaction_id,
            )
            return None

        currency = transaction.currency or "EUR"

        result = self.calculator.calculate(
            amount=transaction.amount,
            fee_rate=classification.fee_rate,
            currency=currency,
            cap=None,
        )

        return self._to_api_result(result)

    def _to_api_result(self, result) -> FeeCalculationResult:
        return FeeCalculationResult(
            amount=result.amount,
            feeRate=result.fee_rate,
            rawFee=result.raw_fee,
            finalFee=result.final_fee,
            currency=result.currency,
            capApplied=result.cap_applied,
            calculationMethod=result.calculation_method,
            finalFeeEur=result.final_fee_eur,
        )