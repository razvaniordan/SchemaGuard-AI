from decimal import Decimal

from core import ConditionEvaluator, ConfidenceScorer
from models import TransactionInput
from rules import EU_PHASE_1_RULE_CATALOGUE


def test_confidence_is_one_for_full_rule_match():
    evaluator = ConditionEvaluator()
    scorer = ConfidenceScorer()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(1)

    transaction = TransactionInput(
        transactionId="txn-full-match",
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

    evaluation = evaluator.evaluate_rule(transaction, rule)
    confidence = scorer.score(evaluation)

    assert evaluation.is_match is True
    assert confidence.score == Decimal("1.00")
    assert confidence.base_score == Decimal("1.00")
    assert confidence.missing_data_penalty == Decimal("0.00")
    assert confidence.unknown_data_penalty == Decimal("0.00")
    assert confidence.missing_fields == []


def test_confidence_penalizes_missing_data():
    evaluator = ConditionEvaluator()
    scorer = ConfidenceScorer()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(1)

    transaction = TransactionInput(
        transactionId="txn-missing-data",
        amount="100.00",
        currency="EUR",
        channel="eCommerce",
        cardType="Credit",
    )

    evaluation = evaluator.evaluate_rule(transaction, rule)
    confidence = scorer.score(evaluation)

    assert evaluation.is_match is False
    assert "authStatus" in confidence.missing_fields
    assert "clearingTime" in confidence.missing_fields
    assert "region" in confidence.missing_fields
    assert confidence.missing_data_penalty == Decimal("0.30")
    assert confidence.score < Decimal("1.00")


def test_confidence_penalty_for_missing_data_is_capped():
    evaluator = ConditionEvaluator()
    scorer = ConfidenceScorer()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(1)

    transaction = TransactionInput(
        transactionId="txn-many-missing-fields"
    )

    evaluation = evaluator.evaluate_rule(transaction, rule)
    confidence = scorer.score(evaluation)

    assert confidence.missing_data_penalty == Decimal("0.30")
    assert confidence.score >= Decimal("0.00")


def test_confidence_uses_default_base_for_any_only_default_rule():
    evaluator = ConditionEvaluator()
    scorer = ConfidenceScorer()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(14)

    transaction = TransactionInput(
        transactionId="txn-default"
    )

    evaluation = evaluator.evaluate_rule(transaction, rule)
    confidence = scorer.score(evaluation)

    assert evaluation.is_match is True
    assert evaluation.applicable_count == 0
    assert confidence.base_score == Decimal("0.50")
    assert confidence.score == Decimal("0.50")


def test_confidence_penalizes_unknown_channel():
    evaluator = ConditionEvaluator()
    scorer = ConfidenceScorer()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(6)

    transaction = TransactionInput(
        transactionId="txn-unknown-channel",
        amount="100.00",
        currency="EUR",
        region="EU",
        channel="not-a-real-channel",
        cardType="Debit",
        authDate="2026-05-05T10:00:00Z",
        clearingDate="2026-05-06T10:00:00Z",
    )

    evaluation = evaluator.evaluate_rule(transaction, rule)
    confidence = scorer.score(evaluation)

    assert evaluation.is_match is False
    assert "UNKNOWN_CHANNEL" in confidence.reason_codes
    assert confidence.unknown_data_penalty == Decimal("0.05")


def test_confidence_logs_missing_data(caplog):
    evaluator = ConditionEvaluator()
    scorer = ConfidenceScorer()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(1)

    transaction = TransactionInput(
        transactionId="txn-logging",
        amount="100.00",
        currency="EUR",
        channel="eCommerce",
        cardType="Credit",
    )

    evaluation = evaluator.evaluate_rule(transaction, rule)

    with caplog.at_level("INFO"):
        confidence = scorer.score(evaluation)

    assert confidence.score < Decimal("1.00")
    assert "Missing data during rule evaluation" in caplog.text
    assert "txn-logging" in caplog.text