from decimal import Decimal

from core import ClearingTimeEvaluator, ConditionEvaluator
from models import ClearingTimeBand, ConditionOutcome, TransactionInput
from rules import EU_PHASE_1_RULE_CATALOGUE


def test_clearing_exactly_24h_is_within_24h():
    evaluator = ClearingTimeEvaluator()

    result = evaluator.evaluate(
        TransactionInput(
            transactionId="txn-clearing-24h",
            authDate="2026-05-05T10:00:00Z",
            clearingDate="2026-05-06T10:00:00Z",
        )
    )

    assert result.band == ClearingTimeBand.WITHIN_24H
    assert result.elapsed_hours == Decimal("24.0")
    assert result.reason_code == "CLEARING_WITHIN_24H"


def test_clearing_over_24h_is_over_24h():
    evaluator = ClearingTimeEvaluator()

    result = evaluator.evaluate(
        TransactionInput(
            transactionId="txn-clearing-over-24h",
            authDate="2026-05-05T10:00:00Z",
            clearingDate="2026-05-06T10:00:01Z",
        )
    )

    assert result.band == ClearingTimeBand.OVER_24H
    assert result.elapsed_hours > Decimal("24")
    assert result.reason_code == "CLEARING_OVER_24H"


def test_date_only_values_are_supported():
    evaluator = ClearingTimeEvaluator()

    result = evaluator.evaluate(
        TransactionInput(
            transactionId="txn-date-only",
            authDate="2026-05-05",
            clearingDate="2026-05-06",
        )
    )

    assert result.band == ClearingTimeBand.WITHIN_24H
    assert result.elapsed_hours == Decimal("24.0")


def test_missing_auth_date_returns_unknown():
    evaluator = ClearingTimeEvaluator()

    result = evaluator.evaluate(
        TransactionInput(
            transactionId="txn-missing-auth-date",
            clearingDate="2026-05-06T10:00:00Z",
        )
    )

    assert result.band == ClearingTimeBand.UNKNOWN
    assert result.reason_code == "MISSING_CLEARING_TIME"


def test_missing_clearing_date_returns_unknown():
    evaluator = ClearingTimeEvaluator()

    result = evaluator.evaluate(
        TransactionInput(
            transactionId="txn-missing-clearing-date",
            authDate="2026-05-05T10:00:00Z",
        )
    )

    assert result.band == ClearingTimeBand.UNKNOWN
    assert result.reason_code == "MISSING_CLEARING_TIME"


def test_clearing_before_auth_returns_unknown_invalid():
    evaluator = ClearingTimeEvaluator()

    result = evaluator.evaluate(
        TransactionInput(
            transactionId="txn-invalid-clearing",
            authDate="2026-05-06T10:00:00Z",
            clearingDate="2026-05-05T10:00:00Z",
        )
    )

    assert result.band == ClearingTimeBand.UNKNOWN
    assert result.reason_code == "INVALID_CLEARING_BEFORE_AUTH"


def test_condition_evaluator_matches_within_24h_rule():
    evaluator = ConditionEvaluator()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(1)

    transaction = TransactionInput(
        transactionId="txn-priority-1",
        amount="100.00",
        currency="EUR",
        region="EU",
        channel="eCommerce",
        cardType="Credit",
        eci="05",
        mcc="5812",
        authDate="2026-05-05T10:00:00Z",
        clearingDate="2026-05-06T10:00:00Z",
    )

    result = evaluator.evaluate_rule(transaction, rule)

    assert result.is_match is True
    assert "clearingTime" in result.matched_conditions


def test_condition_evaluator_rejects_within_24h_rule_when_over_24h():
    evaluator = ConditionEvaluator()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(1)

    transaction = TransactionInput(
        transactionId="txn-priority-1-over-24h",
        amount="100.00",
        currency="EUR",
        region="EU",
        channel="eCommerce",
        cardType="Credit",
        eci="05",
        mcc="5812",
        authDate="2026-05-05T10:00:00Z",
        clearingDate="2026-05-06T10:00:01Z",
    )

    result = evaluator.evaluate_rule(transaction, rule)

    assert result.is_match is False
    assert "CLEARING_TIME_MISMATCH" in result.reason_codes

    clearing_condition = next(
        condition
        for condition in result.condition_results
        if condition.field == "clearingTime"
    )

    assert clearing_condition.outcome == ConditionOutcome.NOT_MATCHED
    assert clearing_condition.expected == "<=24h"
    assert clearing_condition.actual == ">24h"


def test_condition_evaluator_matches_over_24h_rule():
    evaluator = ConditionEvaluator()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(2)

    transaction = TransactionInput(
        transactionId="txn-priority-2",
        amount="100.00",
        currency="EUR",
        region="EU",
        channel="eCommerce",
        cardType="Credit",
        eci="05",
        mcc="5812",
        authDate="2026-05-05T10:00:00Z",
        clearingDate="2026-05-06T10:00:01Z",
    )

    result = evaluator.evaluate_rule(transaction, rule)

    assert result.is_match is True
    assert "clearingTime" in result.matched_conditions