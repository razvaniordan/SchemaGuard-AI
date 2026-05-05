from decimal import Decimal

import pytest

from models import (
    CardType,
    Channel,
    InterchangeCategory,
    Region,
)
from rules import (
    DEFAULT_RULE_PRIORITY,
    EXPECTED_RULE_PRIORITIES,
    EU_PHASE_1_RULE_CATALOGUE,
    PriorityRuleCatalogue,
)


def test_catalogue_contains_14_rules():
    assert len(EU_PHASE_1_RULE_CATALOGUE) == 14


def test_catalogue_priorities_are_1_to_14_in_order():
    priorities = [
        rule.priority
        for rule in EU_PHASE_1_RULE_CATALOGUE.iter_by_priority()
    ]

    assert priorities == list(EXPECTED_RULE_PRIORITIES)


def test_priority_1_is_ecommerce_secure_preferred_credit():
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(1)

    assert rule.priority == 1
    assert rule.channel == Channel.ECOMMERCE
    assert rule.card_type == CardType.CREDIT
    assert rule.region == Region.EU
    assert rule.category == InterchangeCategory.ECOM_SECURE_PREFERRED_CREDIT
    assert rule.category_code == "ECOM_SECURE_PREFERRED_CREDIT"
    assert rule.fee_rate == Decimal("0.0125")
    assert rule.fee_rate_percent == Decimal("1.25")
    assert rule.fee_rate_bps == 125


def test_priority_10_is_cross_border_credit():
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(10)

    assert rule.priority == 10
    assert rule.channel.value == "Any"
    assert rule.card_type == CardType.CREDIT
    assert rule.region == Region.CROSS_BORDER
    assert rule.category == InterchangeCategory.CROSS_BORDER_CREDIT
    assert rule.fee_rate_percent == Decimal("2.50")


def test_priority_13_is_grocery_preferred_mcc():
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(13)

    assert rule.priority == 13
    assert rule.mcc == "5411"
    assert rule.region == Region.EU
    assert rule.category == InterchangeCategory.MCC_PREFERRED_GROCERY
    assert rule.fee_rate_percent == Decimal("0.15")


def test_priority_14_is_default_fallback():
    rule = EU_PHASE_1_RULE_CATALOGUE.get_default_rule()

    assert rule.priority == DEFAULT_RULE_PRIORITY
    assert rule.category == InterchangeCategory.DEFAULT_STANDARD_CATEGORY
    assert rule.category_code == "DEFAULT_STANDARD_CATEGORY"
    assert rule.fee_rate_percent == Decimal("1.75")


def test_get_by_priority_returns_none_for_unknown_priority():
    assert EU_PHASE_1_RULE_CATALOGUE.get_by_priority(99) is None


def test_get_required_by_priority_raises_for_unknown_priority():
    with pytest.raises(KeyError):
        EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(99)


def test_catalogue_rejects_missing_priority():
    incomplete_rules = [
        rule
        for rule in EU_PHASE_1_RULE_CATALOGUE.get_all()
        if rule.priority != 2
    ]

    with pytest.raises(ValueError, match="Missing=\\[2\\]"):
        PriorityRuleCatalogue(incomplete_rules)


def test_catalogue_rejects_duplicate_priority():
    rules = list(EU_PHASE_1_RULE_CATALOGUE.get_all())
    rules[1] = rules[1].model_copy(update={"priority": 1})

    with pytest.raises(ValueError, match="duplicate priorities"):
        PriorityRuleCatalogue(rules)