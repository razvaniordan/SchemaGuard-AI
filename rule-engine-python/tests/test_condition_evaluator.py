from decimal import Decimal

from core import ConditionEvaluator
from models import ConditionOutcome, TransactionInput
from rules import EU_PHASE_1_RULE_CATALOGUE


def test_evaluates_priority_1_as_match_for_secure_ecommerce_credit_within_24h():
    evaluator = ConditionEvaluator()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(1)

    transaction = TransactionInput(
        transactionId="txn-1",
        amount="100.00",
        currency="EUR",
        region="EU",
        channel="eCommerce",
        cardType="Credit",
        threeDS=True,
        eci="05",
        mcc="5812",
        authDate="2026-05-05T10:00:00Z",
        clearingDate="2026-05-06T10:00:00Z",
    )

    result = evaluator.evaluate_rule(transaction, rule)

    assert result.is_match is True
    assert result.missing_fields == []
    assert "channel" in result.matched_conditions
    assert "authStatus" in result.matched_conditions
    assert "clearingTime" in result.matched_conditions
    assert "cardType" in result.matched_conditions
    assert "region" in result.matched_conditions
    assert result.confidence_basis == Decimal("1")


def test_evaluates_priority_1_as_not_match_when_clearing_is_over_24h():
    evaluator = ConditionEvaluator()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(1)

    transaction = TransactionInput(
        transactionId="txn-2",
        amount="100.00",
        currency="EUR",
        region="EU",
        channel="eCommerce",
        cardType="Credit",
        threeDS=True,
        eci="05",
        mcc="5812",
        authDate="2026-05-05T10:00:00Z",
        clearingDate="2026-05-06T10:00:01Z",
    )

    result = evaluator.evaluate_rule(transaction, rule)

    assert result.is_match is False
    assert "CLEARING_TIME_MISMATCH" in result.reason_codes

    clearing_result = next(
        condition
        for condition in result.condition_results
        if condition.field == "clearingTime"
    )

    assert clearing_result.outcome == ConditionOutcome.NOT_MATCHED
    assert clearing_result.expected == "<=24h"
    assert clearing_result.actual == ">24h"


def test_evaluates_missing_data_without_crashing():
    evaluator = ConditionEvaluator()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(1)

    transaction = TransactionInput(
        transactionId="txn-3",
        amount="100.00",
        currency="EUR",
        channel="eCommerce",
        cardType="Credit",
    )

    result = evaluator.evaluate_rule(transaction, rule)

    assert result.is_match is False
    assert "authStatus" in result.missing_fields
    assert "clearingTime" in result.missing_fields
    assert "region" in result.missing_fields
    assert "MISSING_AUTH_STATUS" in result.reason_codes
    assert "MISSING_CLEARING_TIME" in result.reason_codes
    assert "MISSING_REGION" in result.reason_codes


def test_any_conditions_are_not_applicable_and_do_not_penalize_rule():
    evaluator = ConditionEvaluator()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(14)

    transaction = TransactionInput(
        transactionId="txn-4",
        amount="100.00",
        currency="EUR",
    )

    result = evaluator.evaluate_rule(transaction, rule)

    assert result.is_match is True
    assert result.missing_fields == []
    assert result.applicable_count == 0
    assert result.confidence_basis == Decimal("1")

    assert all(
        condition.outcome == ConditionOutcome.NOT_APPLICABLE
        for condition in result.condition_results
    )


def test_grocery_mcc_rule_matches_5411_in_eu():
    evaluator = ConditionEvaluator()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(13)

    transaction = TransactionInput(
        transactionId="txn-5",
        amount="100.00",
        currency="EUR",
        region="EU",
        channel="POS",
        cardType="Debit",
        mcc="5411",
    )

    result = evaluator.evaluate_rule(transaction, rule)

    assert result.is_match is True
    assert "mcc" in result.matched_conditions
    assert "region" in result.matched_conditions


def test_grocery_mcc_rule_does_not_match_wrong_mcc():
    evaluator = ConditionEvaluator()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(13)

    transaction = TransactionInput(
        transactionId="txn-6",
        amount="100.00",
        currency="EUR",
        region="EU",
        channel="POS",
        cardType="Debit",
        mcc="5812",
    )

    result = evaluator.evaluate_rule(transaction, rule)

    assert result.is_match is False
    assert "MCC_MISMATCH" in result.reason_codes


def test_region_can_be_inferred_as_eu_from_country_codes():
    evaluator = ConditionEvaluator()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(7)

    transaction = TransactionInput(
        transactionId="txn-7",
        amount="100.00",
        currency="EUR",
        merchantCountry="RO",
        issuerCountry="DE",
        channel="POS",
        cardType="Credit",
        authDate="2026-05-05T10:00:00Z",
        clearingDate="2026-05-06T09:00:00Z",
    )

    result = evaluator.evaluate_rule(transaction, rule)

    assert result.is_match is True
    assert "region" in result.matched_conditions


def test_auth_status_secure_can_be_derived_from_eci_06():
    evaluator = ConditionEvaluator()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(4)

    transaction = TransactionInput(
        transactionId="txn-8",
        amount="100.00",
        currency="EUR",
        region="EU",
        channel="eCommerce",
        cardType="Debit",
        eci="06",
        authDate="2026-05-05T10:00:00Z",
        clearingDate="2026-05-07T10:00:00Z",
    )

    result = evaluator.evaluate_rule(transaction, rule)

    assert result.is_match is True
    assert "authStatus" in result.matched_conditions