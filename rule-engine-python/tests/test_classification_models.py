from decimal import Decimal

from models.classification_models import (
    CardType,
    Channel,
    EU_PHASE_1_CATEGORY_DEFINITIONS,
    InterchangeCategory,
    Region,
    TransactionInput,
)


def test_transaction_input_normalizes_java_style_payload():
    transaction = TransactionInput(
        transactionId="txn-1",
        amount="100.00",
        currency="eur",
        country="nl",
        channel="ecommerce",
        cardType="credit",
        mcc=5411,
        threeDS=True,
        eci=5,
        authDate="2026-05-05",
        clearingDate="2026-05-06",
    )

    assert transaction.transaction_id == "txn-1"
    assert transaction.amount == Decimal("100.00")
    assert transaction.currency == "EUR"
    assert transaction.country == "NL"
    assert transaction.channel == Channel.ECOMMERCE
    assert transaction.card_type == CardType.CREDIT
    assert transaction.mcc == "5411"
    assert transaction.eci == "05"


def test_phase_1_definitions_cover_priorities_1_to_14():
    priorities = [definition.priority for definition in EU_PHASE_1_CATEGORY_DEFINITIONS]

    assert priorities == list(range(1, 15))


def test_phase_1_default_category_is_priority_14():
    default = EU_PHASE_1_CATEGORY_DEFINITIONS[-1]

    assert default.priority == 14
    assert default.category == InterchangeCategory.DEFAULT_STANDARD_CATEGORY
    assert default.fee_rate == Decimal("0.0175")


def test_region_and_card_type_aliases_are_supported():
    transaction = TransactionInput(
        region="cross_border",
        cardType="business",
        channel="card-present",
    )

    assert transaction.region == Region.CROSS_BORDER
    assert transaction.card_type == CardType.COMMERCIAL
    assert transaction.channel == Channel.POS