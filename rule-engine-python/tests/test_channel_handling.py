from core import ConditionEvaluator
from models import Channel, ConditionOutcome, TransactionInput
from rules import EU_PHASE_1_RULE_CATALOGUE


def test_channel_match_case_handles_pos_channel():
    evaluator = ConditionEvaluator()

    result = evaluator.evaluate_channel(
        TransactionInput(transactionId="txn-pos", channel="POS"),
        Channel.POS,
    )

    assert result.outcome == ConditionOutcome.MATCHED
    assert result.field == "channel"
    assert result.expected == "POS"
    assert result.actual == "POS"


def test_channel_match_case_handles_ecommerce_channel():
    evaluator = ConditionEvaluator()

    result = evaluator.evaluate_channel(
        TransactionInput(transactionId="txn-ecom", channel="eCommerce"),
        Channel.ECOMMERCE,
    )

    assert result.outcome == ConditionOutcome.MATCHED
    assert result.field == "channel"
    assert result.expected == "eCommerce"
    assert result.actual == "eCommerce"


def test_channel_match_case_handles_moto_channel():
    evaluator = ConditionEvaluator()

    result = evaluator.evaluate_channel(
        TransactionInput(transactionId="txn-moto", channel="MOTO"),
        Channel.MOTO,
    )

    assert result.outcome == ConditionOutcome.MATCHED
    assert result.field == "channel"
    assert result.expected == "MOTO"
    assert result.actual == "MOTO"


def test_channel_any_is_not_applicable():
    evaluator = ConditionEvaluator()

    result = evaluator.evaluate_channel(
        TransactionInput(transactionId="txn-any", channel="POS"),
        Channel.ANY,
    )

    assert result.outcome == ConditionOutcome.NOT_APPLICABLE
    assert result.expected == "Any"
    assert result.actual == "POS"


def test_channel_missing_returns_missing_result():
    evaluator = ConditionEvaluator()

    result = evaluator.evaluate_channel(
        TransactionInput(transactionId="txn-missing"),
        Channel.POS,
    )

    assert result.outcome == ConditionOutcome.MISSING
    assert result.reason_code == "MISSING_CHANNEL"


def test_channel_unknown_returns_unknown_channel_reason_code():
    evaluator = ConditionEvaluator()

    result = evaluator.evaluate_channel(
        TransactionInput(transactionId="txn-unknown", channel="unknown-channel"),
        Channel.POS,
    )

    assert result.outcome == ConditionOutcome.NOT_MATCHED
    assert result.reason_code == "UNKNOWN_CHANNEL"
    assert result.actual == "Unknown"


def test_channel_mismatch_returns_channel_mismatch():
    evaluator = ConditionEvaluator()

    result = evaluator.evaluate_channel(
        TransactionInput(transactionId="txn-mismatch", channel="MOTO"),
        Channel.ECOMMERCE,
    )

    assert result.outcome == ConditionOutcome.NOT_MATCHED
    assert result.reason_code == "CHANNEL_MISMATCH"
    assert result.expected == "eCommerce"
    assert result.actual == "MOTO"


def test_moto_credit_rule_uses_channel_handling_correctly():
    evaluator = ConditionEvaluator()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(8)

    transaction = TransactionInput(
        transactionId="txn-moto-credit",
        amount="100.00",
        currency="EUR",
        channel="MOTO",
        cardType="Credit",
    )

    result = evaluator.evaluate_rule(transaction, rule)

    assert result.is_match is True
    assert "channel" in result.matched_conditions


def test_moto_credit_rule_rejects_ecommerce_channel():
    evaluator = ConditionEvaluator()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(8)

    transaction = TransactionInput(
        transactionId="txn-ecom-credit",
        amount="100.00",
        currency="EUR",
        channel="eCommerce",
        cardType="Credit",
    )

    result = evaluator.evaluate_rule(transaction, rule)

    assert result.is_match is False
    assert "CHANNEL_MISMATCH" in result.reason_codes