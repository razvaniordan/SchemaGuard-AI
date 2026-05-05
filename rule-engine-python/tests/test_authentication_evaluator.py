from core import AuthenticationEvaluator, ConditionEvaluator
from models import AuthStatus, ConditionOutcome, TransactionInput
from rules import EU_PHASE_1_RULE_CATALOGUE


def test_eci_05_is_secure():
    evaluator = AuthenticationEvaluator()

    result = evaluator.evaluate(
        TransactionInput(transactionId="txn-eci-05", eci="05")
    )

    assert result.status == AuthStatus.SECURE
    assert result.source == "eci"
    assert result.reason_code == "SECURE_ECI"


def test_eci_06_is_secure():
    evaluator = AuthenticationEvaluator()

    result = evaluator.evaluate(
        TransactionInput(transactionId="txn-eci-06", eci="06")
    )

    assert result.status == AuthStatus.SECURE
    assert result.source == "eci"
    assert result.reason_code == "SECURE_ECI"


def test_non_secure_eci_is_non_secure():
    evaluator = AuthenticationEvaluator()

    result = evaluator.evaluate(
        TransactionInput(transactionId="txn-eci-07", eci="07")
    )

    assert result.status == AuthStatus.NON_SECURE
    assert result.source == "eci"
    assert result.reason_code == "NON_SECURE_ECI"


def test_eci_takes_priority_over_three_ds_flag():
    evaluator = AuthenticationEvaluator()

    result = evaluator.evaluate(
        TransactionInput(
            transactionId="txn-conflict",
            eci="07",
            threeDS=True,
        )
    )

    assert result.status == AuthStatus.NON_SECURE
    assert result.source == "eci"
    assert result.reason_code == "NON_SECURE_ECI"


def test_three_ds_true_is_secure_when_eci_is_missing():
    evaluator = AuthenticationEvaluator()

    result = evaluator.evaluate(
        TransactionInput(
            transactionId="txn-three-ds-true",
            threeDS=True,
        )
    )

    assert result.status == AuthStatus.SECURE
    assert result.source == "threeDS"
    assert result.reason_code == "SECURE_THREEDS_FLAG"


def test_three_ds_false_is_non_secure_when_eci_is_missing():
    evaluator = AuthenticationEvaluator()

    result = evaluator.evaluate(
        TransactionInput(
            transactionId="txn-three-ds-false",
            threeDS=False,
        )
    )

    assert result.status == AuthStatus.NON_SECURE
    assert result.source == "threeDS"
    assert result.reason_code == "NON_SECURE_THREEDS_FLAG"


def test_missing_eci_and_three_ds_returns_unknown():
    evaluator = AuthenticationEvaluator()

    result = evaluator.evaluate(
        TransactionInput(transactionId="txn-missing-auth")
    )

    assert result.status == AuthStatus.UNKNOWN
    assert result.source == "missing"
    assert result.reason_code == "MISSING_AUTH_STATUS"


def test_condition_evaluator_matches_secure_ecommerce_debit_with_eci_06():
    evaluator = ConditionEvaluator()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(4)

    transaction = TransactionInput(
        transactionId="txn-ecom-secure-debit",
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


def test_condition_evaluator_rejects_secure_rule_for_non_secure_eci():
    evaluator = ConditionEvaluator()
    rule = EU_PHASE_1_RULE_CATALOGUE.get_required_by_priority(1)

    transaction = TransactionInput(
        transactionId="txn-ecom-non-secure-credit",
        amount="100.00",
        currency="EUR",
        region="EU",
        channel="eCommerce",
        cardType="Credit",
        eci="07",
        authDate="2026-05-05T10:00:00Z",
        clearingDate="2026-05-06T10:00:00Z",
    )

    result = evaluator.evaluate_rule(transaction, rule)

    assert result.is_match is False
    assert "AUTH_STATUS_MISMATCH" in result.reason_codes

    auth_condition = next(
        condition
        for condition in result.condition_results
        if condition.field == "authStatus"
    )

    assert auth_condition.outcome == ConditionOutcome.NOT_MATCHED
    assert auth_condition.expected == "Secure"
    assert auth_condition.actual == "Non-Secure"