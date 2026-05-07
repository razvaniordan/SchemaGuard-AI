from datetime import datetime, timezone
from decimal import Decimal

from core import FeeCalculationService
from models import (
    ClassificationResult,
    FeeCalculationRequest,
    InterchangeCategory,
    TransactionInput,
)


def _classification_result() -> ClassificationResult:
    return ClassificationResult(
        transactionId="txn-fee",
        category=InterchangeCategory.ECOM_SECURE_PREFERRED_CREDIT,
        categoryCode="ECOM_SECURE_PREFERRED_CREDIT",
        rulePriority=1,
        feeRate=Decimal("0.0125"),
        feeRatePercent=Decimal("1.25"),
        feeRateBps=125,
        confidence=Decimal("1.00"),
        explanation="Classified as Ecom Secure Preferred Credit.",
        classifiedAt=datetime(2026, 5, 5, 12, 0, tzinfo=timezone.utc),
    )


def test_fee_service_calculates_from_standalone_request():
    service = FeeCalculationService()

    result = service.calculate(
        FeeCalculationRequest(
            amount=Decimal("100.00"),
            feeRate=Decimal("0.0125"),
            currency="EUR",
        )
    )

    assert result.amount == Decimal("100.00")
    assert result.fee_rate == Decimal("0.0125")
    assert result.raw_fee == Decimal("1.25")
    assert result.final_fee == Decimal("1.25")
    assert result.currency == "EUR"
    assert result.final_fee_eur is None


def test_fee_service_calculates_for_classification():
    service = FeeCalculationService()

    transaction = TransactionInput(
        transactionId="txn-fee",
        amount="100.00",
        currency="EUR",
    )

    result = service.calculate_for_classification(
        transaction=transaction,
        classification=_classification_result(),
    )

    assert result is not None
    assert result.raw_fee == Decimal("1.25")
    assert result.final_fee == Decimal("1.25")
    assert result.currency == "EUR"


def test_fee_service_returns_none_when_transaction_amount_is_missing():
    service = FeeCalculationService()

    transaction = TransactionInput(
        transactionId="txn-no-amount",
        currency="EUR",
    )

    result = service.calculate_for_classification(
        transaction=transaction,
        classification=_classification_result(),
    )

    assert result is None


def test_fee_service_applies_caps():
    service = FeeCalculationService()

    result = service.calculate(
        FeeCalculationRequest(
            amount=Decimal("100.00"),
            feeRate=Decimal("0.01"),
            currency="EUR",
            cap={
                "minFee": Decimal("2.00"),
                "maxFee": Decimal("10.00"),
            },
        )
    )

    assert result.raw_fee == Decimal("1.00")
    assert result.final_fee == Decimal("2.00")
    assert result.cap_applied == "MIN_FEE"