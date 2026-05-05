"""Card type strategy pattern for interchange classification.

Story 2.2.8: Card type strategy pattern.

Each supported card type has a dedicated strategy. The ConditionEvaluator
delegates card type evaluation to this module instead of hard-coding all
matching logic directly.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from models import CardType, ConditionOutcome, TransactionInput

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CardTypeEvaluation:
    """Result of evaluating a transaction card type against an expected type."""

    expected: CardType
    actual: CardType | None
    outcome: ConditionOutcome
    reason_code: str | None = None
    message: str | None = None


class CardTypeStrategy(ABC):
    """Base class for card type matching strategies."""

    expected_type: CardType

    @abstractmethod
    def evaluate(self, transaction: TransactionInput) -> CardTypeEvaluation:
        """Evaluate the transaction against the strategy's expected card type."""


class AnyCardTypeStrategy(CardTypeStrategy):
    expected_type = CardType.ANY

    def evaluate(self, transaction: TransactionInput) -> CardTypeEvaluation:
        return CardTypeEvaluation(
            expected=self.expected_type,
            actual=transaction.card_type,
            outcome=ConditionOutcome.NOT_APPLICABLE,
            message="Rule accepts any card type.",
        )


class CreditCardTypeStrategy(CardTypeStrategy):
    expected_type = CardType.CREDIT

    def evaluate(self, transaction: TransactionInput) -> CardTypeEvaluation:
        return _evaluate_exact_card_type(
            transaction=transaction,
            expected=self.expected_type,
            missing_reason_code="MISSING_CARD_TYPE",
            mismatch_reason_code="CARD_TYPE_MISMATCH",
            matched_message="Credit card type matched.",
            mismatch_message="Expected Credit card type.",
        )


class DebitCardTypeStrategy(CardTypeStrategy):
    expected_type = CardType.DEBIT

    def evaluate(self, transaction: TransactionInput) -> CardTypeEvaluation:
        return _evaluate_exact_card_type(
            transaction=transaction,
            expected=self.expected_type,
            missing_reason_code="MISSING_CARD_TYPE",
            mismatch_reason_code="CARD_TYPE_MISMATCH",
            matched_message="Debit card type matched.",
            mismatch_message="Expected Debit card type.",
        )


class CommercialCardTypeStrategy(CardTypeStrategy):
    expected_type = CardType.COMMERCIAL

    def evaluate(self, transaction: TransactionInput) -> CardTypeEvaluation:
        return _evaluate_exact_card_type(
            transaction=transaction,
            expected=self.expected_type,
            missing_reason_code="MISSING_CARD_TYPE",
            mismatch_reason_code="CARD_TYPE_MISMATCH",
            matched_message="Commercial card type matched.",
            mismatch_message="Expected Commercial card type.",
        )


class PrepaidCardTypeStrategy(CardTypeStrategy):
    expected_type = CardType.PREPAID

    def evaluate(self, transaction: TransactionInput) -> CardTypeEvaluation:
        return _evaluate_exact_card_type(
            transaction=transaction,
            expected=self.expected_type,
            missing_reason_code="MISSING_CARD_TYPE",
            mismatch_reason_code="CARD_TYPE_MISMATCH",
            matched_message="Prepaid card type matched.",
            mismatch_message="Expected Prepaid card type.",
        )


class UnknownCardTypeStrategy(CardTypeStrategy):
    expected_type = CardType.UNKNOWN

    def evaluate(self, transaction: TransactionInput) -> CardTypeEvaluation:
        logger.info(
            "Unknown expected card type for transaction_id=%s actual_card_type=%s",
            transaction.transaction_id,
            transaction.card_type,
        )

        return CardTypeEvaluation(
            expected=self.expected_type,
            actual=transaction.card_type,
            outcome=ConditionOutcome.NOT_MATCHED,
            reason_code="UNKNOWN_EXPECTED_CARD_TYPE",
            message="Expected card type is unknown.",
        )


class CardTypeStrategyRegistry:
    """Registry/factory for card type strategies."""

    def __init__(self) -> None:
        self._strategies: dict[CardType, CardTypeStrategy] = {
            CardType.ANY: AnyCardTypeStrategy(),
            CardType.CREDIT: CreditCardTypeStrategy(),
            CardType.DEBIT: DebitCardTypeStrategy(),
            CardType.COMMERCIAL: CommercialCardTypeStrategy(),
            CardType.PREPAID: PrepaidCardTypeStrategy(),
            CardType.UNKNOWN: UnknownCardTypeStrategy(),
        }

    def get_strategy(self, expected: CardType) -> CardTypeStrategy:
        """Return the strategy for the expected card type."""

        return self._strategies.get(expected, UnknownCardTypeStrategy())

    def evaluate(
        self,
        transaction: TransactionInput,
        expected: CardType,
    ) -> CardTypeEvaluation:
        """Evaluate transaction card type using the matching strategy."""

        strategy = self.get_strategy(expected)
        return strategy.evaluate(transaction)


def _evaluate_exact_card_type(
    *,
    transaction: TransactionInput,
    expected: CardType,
    missing_reason_code: str,
    mismatch_reason_code: str,
    matched_message: str,
    mismatch_message: str,
) -> CardTypeEvaluation:
    """Shared exact-match logic for concrete card type strategies."""

    actual = transaction.card_type

    if actual is None:
        logger.info(
            "Missing card type for transaction_id=%s",
            transaction.transaction_id,
        )

        return CardTypeEvaluation(
            expected=expected,
            actual=None,
            outcome=ConditionOutcome.MISSING,
            reason_code=missing_reason_code,
            message="cardType is missing.",
        )

    if actual == CardType.UNKNOWN:
        logger.info(
            "Unknown card type for transaction_id=%s",
            transaction.transaction_id,
        )

        return CardTypeEvaluation(
            expected=expected,
            actual=actual,
            outcome=ConditionOutcome.NOT_MATCHED,
            reason_code="UNKNOWN_CARD_TYPE",
            message="Transaction card type is unknown.",
        )

    if actual == expected:
        return CardTypeEvaluation(
            expected=expected,
            actual=actual,
            outcome=ConditionOutcome.MATCHED,
            message=matched_message,
        )

    return CardTypeEvaluation(
        expected=expected,
        actual=actual,
        outcome=ConditionOutcome.NOT_MATCHED,
        reason_code=mismatch_reason_code,
        message=mismatch_message,
    )