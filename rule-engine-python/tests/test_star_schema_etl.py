from datetime import datetime, timezone
from decimal import Decimal

from core import StarSchemaETL, UNKNOWN_DIMENSION_KEY
from models import (
    ClassificationResult,
    InterchangeCategory,
    TransactionInput,
)


def _classification_result(
    *,
    transaction_id: str = "txn-1",
    classified_at: datetime | None = None,
) -> ClassificationResult:
    return ClassificationResult(
        transactionId=transaction_id,
        category=InterchangeCategory.ECOM_SECURE_PREFERRED_CREDIT,
        categoryCode="ECOM_SECURE_PREFERRED_CREDIT",
        rulePriority=1,
        feeRate=Decimal("0.0125"),
        feeRatePercent=Decimal("1.25"),
        feeRateBps=125,
        confidence=Decimal("0.95"),
        matchedConditions=[
            "channel",
            "authStatus",
            "clearingTime",
            "cardType",
            "region",
        ],
        missingFields=[],
        reasonCodes=[],
        conditionResults=[],
        explanation="Classified as Ecom Secure Preferred Credit.",
        classifiedAt=classified_at or datetime(2026, 5, 5, 12, 0, tzinfo=timezone.utc),
    )


def test_etl_maps_transaction_and_classification_to_fact_transaction():
    etl = StarSchemaETL()

    transaction = TransactionInput(
        transactionId="txn-1",
        merchantId="merchant-123",
        cardId="card-456",
        amount="100.00",
        currency="EUR",
        region="EU",
        channel="eCommerce",
        cardType="Credit",
        mcc="5411",
        authDate="2026-05-05T10:00:00Z",
        clearingDate="2026-05-06T10:00:00Z",
    )

    classification = _classification_result(transaction_id="txn-1")

    fact = etl.to_fact_transaction(
        transaction=transaction,
        classification=classification,
    )

    assert fact.fact_transaction_id == "fact-txn-1"
    assert fact.transaction_id == "txn-1"

    assert fact.dim_merchant_key != UNKNOWN_DIMENSION_KEY
    assert fact.dim_card_key != UNKNOWN_DIMENSION_KEY
    assert fact.dim_channel_key == 2
    assert fact.dim_region_key == 1
    assert fact.dim_date_key == 20260505
    assert fact.dim_category_key != UNKNOWN_DIMENSION_KEY

    assert fact.amount == Decimal("100.00")
    assert fact.currency == "EUR"
    assert fact.category_code == "ECOM_SECURE_PREFERRED_CREDIT"
    assert fact.fee_rate == Decimal("0.0125")
    assert fact.confidence == Decimal("0.95")
    assert fact.rule_priority == 1


def test_etl_generates_deterministic_dimension_keys():
    etl = StarSchemaETL()

    transaction = TransactionInput(
        transactionId="txn-1",
        merchantId="merchant-123",
        cardId="card-456",
        amount="100.00",
        currency="EUR",
        region="EU",
        channel="eCommerce",
        authDate="2026-05-05T10:00:00Z",
    )

    classification = _classification_result(transaction_id="txn-1")

    fact_1 = etl.to_fact_transaction(
        transaction=transaction,
        classification=classification,
    )

    fact_2 = etl.to_fact_transaction(
        transaction=transaction,
        classification=classification,
    )

    assert fact_1.dim_merchant_key == fact_2.dim_merchant_key
    assert fact_1.dim_card_key == fact_2.dim_card_key
    assert fact_1.dim_category_key == fact_2.dim_category_key


def test_etl_uses_classified_at_when_auth_date_is_missing():
    etl = StarSchemaETL()

    classified_at = datetime(2026, 6, 10, 15, 30, tzinfo=timezone.utc)

    transaction = TransactionInput(
        transactionId="txn-no-auth-date",
        merchantId="merchant-123",
        cardId="card-456",
        amount="50.00",
        currency="EUR",
        region="EU",
        channel="POS",
    )

    classification = _classification_result(
        transaction_id="txn-no-auth-date",
        classified_at=classified_at,
    )

    fact = etl.to_fact_transaction(
        transaction=transaction,
        classification=classification,
    )

    assert fact.dim_date_key == 20260610


def test_etl_handles_missing_dimension_values_without_crashing():
    etl = StarSchemaETL()

    transaction = TransactionInput(
        transactionId="txn-missing-dimensions",
        amount="25.00",
        currency="EUR",
    )

    classification = _classification_result(transaction_id="txn-missing-dimensions")

    fact = etl.to_fact_transaction(
        transaction=transaction,
        classification=classification,
    )

    assert fact.fact_transaction_id == "fact-txn-missing-dimensions"
    assert fact.dim_merchant_key == UNKNOWN_DIMENSION_KEY
    assert fact.dim_card_key == UNKNOWN_DIMENSION_KEY
    assert fact.dim_channel_key == UNKNOWN_DIMENSION_KEY
    assert fact.dim_region_key == UNKNOWN_DIMENSION_KEY
    assert fact.dim_date_key == 20260505


def test_etl_uses_classification_transaction_id_when_transaction_id_is_missing():
    etl = StarSchemaETL()

    transaction = TransactionInput(
        amount="25.00",
        currency="EUR",
        region="EU",
        channel="MOTO",
    )

    classification = _classification_result(transaction_id="classification-txn-id")

    fact = etl.to_fact_transaction(
        transaction=transaction,
        classification=classification,
    )

    assert fact.transaction_id == "classification-txn-id"
    assert fact.fact_transaction_id == "fact-classification-txn-id"
    assert fact.dim_channel_key == 3
    assert fact.dim_region_key == 1


def test_etl_serializes_using_java_friendly_aliases():
    etl = StarSchemaETL()

    transaction = TransactionInput(
        transactionId="txn-json",
        merchantId="merchant-123",
        cardId="card-456",
        amount="100.00",
        currency="EUR",
        region="EU",
        channel="eCommerce",
        authDate="2026-05-05T10:00:00Z",
    )

    classification = _classification_result(transaction_id="txn-json")

    fact = etl.to_fact_transaction(
        transaction=transaction,
        classification=classification,
    )

    payload = fact.model_dump(by_alias=True, mode="json")

    assert payload["factTransactionId"] == "fact-txn-json"
    assert payload["transactionId"] == "txn-json"
    assert payload["dimMerchantKey"] == fact.dim_merchant_key
    assert payload["dimCardKey"] == fact.dim_card_key
    assert payload["dimChannelKey"] == 2
    assert payload["dimRegionKey"] == 1
    assert payload["dimDateKey"] == 20260505
    assert payload["categoryCode"] == "ECOM_SECURE_PREFERRED_CREDIT"
    assert payload["rulePriority"] == 1