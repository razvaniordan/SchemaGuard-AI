from core import ConditionEvaluator
from models import CardType, ConditionOutcome, TransactionInput
from rules import EU_PHASE_1_RULE_CATALOGUE
from strategies import CardTypeStrategyRegistry


def test_credit_card_strategy_matches_credit():
    registry = CardTypeStrategyRegistry()

    result = registry.evaluate(
        transaction=TransactionInput(transactionId="txn-credit", cardType="Credit"),
        expected=CardType.CREDIT,
    )

    assert result.outcome == ConditionOutcome.MATCHED
    assert result.expected == CardType.CREDIT
    assert result.actual == CardType.CREDIT


def test_debit_card_strategy_matches_debit():
    registry = CardTypeStrategyRegistry()

    result = registry.evaluate(
        transaction=TransactionInput(transactionId="txn-debit", cardType="Debit"),
        expected=CardType.DEBIT,
    )

    assert result.outcome == ConditionOutcome.MATCHED
    assert result.expected == CardType.DEBIT
    assert result.actual == CardType.DEBIT


def test_commercial_card_strategy_matches_business_alias():
    registry = CardTypeStrategyRegistry()

    result = registry.evaluate(
        transaction=TransactionInput(transactionId="txn-business", cardType="Business"),
        expected=CardType.COMMERCIAL,
    )

    assert result.outcome == ConditionOutcome.MATCHED
    assert result.expected == CardType.COMMERCIAL
    assert result.actual == CardType.COMMERCIAL


def test_prepaid_card_strategy_matches_prepaid():
    registry = CardTypeStrategyRegistry()

    result = registry.evaluate(
        transaction=TransactionInput(transactionId="txn-prepaid", cardType="Prepaid"),
        expected=CardType.PREPAID,
    )

    assert result.outcome == ConditionOutcome.MATCHED
    assert result.expected == CardType.PREPAID
    assert result.actual == CardType.PREPAID


def test_any_card_type_strategy_is_not_applicable():
    registry = CardTypeStrategyRegistry()

    result = registry.evaluate(
        transaction=TransactionInput(transactionId="txn-any", cardType="Credit"),
        expected=CardType.ANY,
    )

    assert result.outcome == ConditionOutcome.NOT_APPLICABLE
    assert result.expected == CardType.ANY
    assert result.actual == CardType.CREDIT


def test_missing_card_type_returns_missing():
    registry = CardTypeStrategyRegistry()

    result = registry.evaluate(
        transaction=TransactionInput(transactionId="txn-missing"),
        expected=CardType.CREDIT,
    )

    assert result.outcome == ConditionOutcome.MISSING
    assert result.expected == CardType.CREDIT
    assert result.actual is None
    assert result.reason_code == "MISSING_CARD_TYPE"


def test_unknown_transaction_card_type_returns_unknown_reason_code():
    registry = CardTypeStrategyRegistry()

    result = registry.evaluate(
        transaction=TransactionInput(transactionId="txn-unknown", cardType="not-a-card-type"),
        expected=CardType.CREDIT,
    )

    assert result.outcome == ConditionOutcome.NOT_MATCHED
    assert result.expected == CardType.CREDIT
    assert result.actual == CardType.UNKNOWN
    assert result.reason_code == "UNKNOWN_CARD_TYPE"


def test_card_type_mismatch_returns_mismatch():
    registry = CardTypeStrategyRegistry()

    result = registry.evaluate(
        transaction=TransactionInput(transactionId="txn-mismatch", cardType="Debit"),
        expected=CardType.CREDIT,
    )

    assert result.outcome == ConditionOutcome.NOT_MATCHED
    assert result.expected == CardType.CREDIT
    assert result.actual == CardType.DEBIT
    assert result.reason_code == "CARD_TYPE_MISMATCH"


def test_condition_evaluator_uses_card_type_strategy_for_credit_rule():
    evaluator = ConditionEvaluator()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(1)

    transaction = TransactionInput(
        transactionId="txn-priority-1-credit",
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
    assert "cardType" in result.matched_conditions


def test_condition_evaluator_uses_card_type_strategy_for_commercial_rule():
    evaluator = ConditionEvaluator()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(12)

    transaction = TransactionInput(
        transactionId="txn-commercial",
        amount="100.00",
        currency="EUR",
        region="EU",
        channel="eCommerce",
        cardType="Business",
        eci="05",
        mcc="5812",
        authDate="2026-05-05T10:00:00Z",
        clearingDate="2026-05-06T10:00:00Z",
    )

    result = evaluator.evaluate_rule(transaction, rule)

    assert result.is_match is True
    assert "cardType" in result.matched_conditions


def test_condition_evaluator_rejects_credit_rule_for_debit_card():
    evaluator = ConditionEvaluator()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(1)

    transaction = TransactionInput(
        transactionId="txn-debit-against-credit",
        amount="100.00",
        currency="EUR",
        region="EU",
        channel="eCommerce",
        cardType="Debit",
        eci="05",
        mcc="5812",
        authDate="2026-05-05T10:00:00Z",
        clearingDate="2026-05-06T10:00:00Z",
    )

    result = evaluator.evaluate_rule(transaction, rule)

    assert result.is_match is False
    assert "CARD_TYPE_MISMATCH" in result.reason_codes

    card_type_condition = next(
        condition
        for condition in result.condition_results
        if condition.field == "cardType"
    )

    assert card_type_condition.outcome == ConditionOutcome.NOT_MATCHED
    assert card_type_condition.expected == "Credit"
    assert card_type_condition.actual == "Debit"