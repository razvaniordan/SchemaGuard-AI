"""Generic condition evaluator for interchange classification rules.
"""


from __future__ import annotations
from .authentication_evaluator import AuthenticationEvaluator
from .clearing_time_evaluator import ClearingTimeEvaluator
import logging
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from decimal import Decimal

from models import (
    AuthStatus,
    CardType,
    CategoryDefinition,
    Channel,
    ClassificationConditionResult,
    ClearingTimeBand,
    ConditionOutcome,
    Region,
    TransactionInput,
)

logger = logging.getLogger(__name__)



EU_COUNTRY_CODES = {
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
    "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL",
    "PL", "PT", "RO", "SK", "SI", "ES", "SE",
}


@dataclass(frozen=True)
class RuleEvaluationResult:
    """Result of evaluating one transaction against one category rule."""

    rule: CategoryDefinition
    is_match: bool
    condition_results: list[ClassificationConditionResult]
    matched_conditions: list[str]
    missing_fields: list[str]
    reason_codes: list[str]
    matched_count: int
    applicable_count: int

    @property
    def confidence_basis(self) -> Decimal:
        """Simple confidence basis for later confidence scoring.

        This is not the final classification confidence yet. It is the ratio of
        matched applicable conditions to all applicable conditions.
        """

        if self.applicable_count == 0:
            return Decimal("1")

        return Decimal(self.matched_count) / Decimal(self.applicable_count)


class ConditionEvaluator:
    """Evaluate transaction attributes against a category definition."""

    def __init__(
        self,
        authentication_evaluator: AuthenticationEvaluator | None = None,
        clearing_time_evaluator: ClearingTimeEvaluator | None = None,
    ) -> None:
        self.authentication_evaluator = (
            authentication_evaluator or AuthenticationEvaluator()
        )
        self.clearing_time_evaluator = (
            clearing_time_evaluator or ClearingTimeEvaluator()
        )

    def evaluate_rule(
        self,
        transaction: TransactionInput,
        rule: CategoryDefinition,
    ) -> RuleEvaluationResult:
        """Evaluate all relevant rule conditions.

        A rule matches only when every applicable condition matches.
        Conditions marked NOT_APPLICABLE do not penalize the rule.
        Missing fields make the rule fail and are recorded for explainability.
        """

        condition_results = [
            self.evaluate_channel(transaction, rule.channel),
            self.evaluate_auth_status(transaction, rule.auth_status),
            self.evaluate_clearing_time(transaction, rule.clearing_time),
            self.evaluate_card_type(transaction, rule.card_type),
            self.evaluate_region(transaction, rule.region),
            self.evaluate_mcc(transaction, rule.mcc),
        ]

        applicable_results = [
            result
            for result in condition_results
            if result.outcome != ConditionOutcome.NOT_APPLICABLE
        ]

        matched_results = [
            result
            for result in applicable_results
            if result.outcome == ConditionOutcome.MATCHED
        ]

        missing_fields = [
            result.field
            for result in condition_results
            if result.outcome == ConditionOutcome.MISSING
        ]

        reason_codes = [
            result.reason_code
            for result in condition_results
            if result.reason_code is not None
        ]

        matched_conditions = [
            result.field
            for result in matched_results
        ]

        is_match = all(
            result.outcome in {
                ConditionOutcome.MATCHED,
                ConditionOutcome.NOT_APPLICABLE,
            }
            for result in condition_results
        )

        return RuleEvaluationResult(
            rule=rule,
            is_match=is_match,
            condition_results=condition_results,
            matched_conditions=matched_conditions,
            missing_fields=missing_fields,
            reason_codes=reason_codes,
            matched_count=len(matched_results),
            applicable_count=len(applicable_results),
        )

    def evaluate_channel(
        self,
        transaction: TransactionInput,
        expected: Channel,
    ) -> ClassificationConditionResult:
        """Evaluate transaction channel using Python match/case.

        Supported business channels:
        - POS
        - eCommerce
        - MOTO

        Channel.ANY is treated as not applicable.
        Missing or unknown channels fail the specific rule and are logged.
        """

        actual = transaction.channel

        match (expected, actual):
            case (Channel.ANY, _):
                return self._not_applicable(
                    field="channel",
                    expected=expected.value,
                    actual=self._enum_value(actual),
                    message="Rule accepts any channel.",
                )

            case (_, None):
                logger.info(
                    "Missing channel for transaction_id=%s",
                    transaction.transaction_id,
                )
                return self._missing(
                    field="channel",
                    expected=expected.value,
                    reason_code="MISSING_CHANNEL",
                )

            case (_, Channel.UNKNOWN):
                logger.info(
                    "Unknown channel for transaction_id=%s",
                    transaction.transaction_id,
                )
                return self._not_matched(
                    field="channel",
                    expected=expected.value,
                    actual=Channel.UNKNOWN.value,
                    reason_code="UNKNOWN_CHANNEL",
                    message="Transaction channel is unknown.",
                )

            case (Channel.POS, Channel.POS):
                return self._matched(
                    field="channel",
                    expected=Channel.POS.value,
                    actual=Channel.POS.value,
                    message="POS channel matched.",
                )

            case (Channel.ECOMMERCE, Channel.ECOMMERCE):
                return self._matched(
                    field="channel",
                    expected=Channel.ECOMMERCE.value,
                    actual=Channel.ECOMMERCE.value,
                    message="eCommerce channel matched.",
                )

            case (Channel.MOTO, Channel.MOTO):
                return self._matched(
                    field="channel",
                    expected=Channel.MOTO.value,
                    actual=Channel.MOTO.value,
                    message="MOTO channel matched.",
                )

            case (Channel.POS, _):
                return self._not_matched(
                    field="channel",
                    expected=Channel.POS.value,
                    actual=self._enum_value(actual),
                    reason_code="CHANNEL_MISMATCH",
                    message="Expected POS channel.",
                )

            case (Channel.ECOMMERCE, _):
                return self._not_matched(
                    field="channel",
                    expected=Channel.ECOMMERCE.value,
                    actual=self._enum_value(actual),
                    reason_code="CHANNEL_MISMATCH",
                    message="Expected eCommerce channel.",
                )

            case (Channel.MOTO, _):
                return self._not_matched(
                    field="channel",
                    expected=Channel.MOTO.value,
                    actual=self._enum_value(actual),
                    reason_code="CHANNEL_MISMATCH",
                    message="Expected MOTO channel.",
                )

            case _:
                logger.warning(
                    "Unsupported channel evaluation expected=%s actual=%s transaction_id=%s",
                    self._enum_value(expected),
                    self._enum_value(actual),
                    transaction.transaction_id,
                )
                return self._not_matched(
                    field="channel",
                    expected=self._enum_value(expected),
                    actual=self._enum_value(actual),
                    reason_code="UNSUPPORTED_CHANNEL_EVALUATION",
                    message="Unsupported channel evaluation.",
                )
    def evaluate_auth_status(
        self,
        transaction: TransactionInput,
        expected: AuthStatus,
    ) -> ClassificationConditionResult:
        auth_evaluation = self.authentication_evaluator.evaluate(transaction)

        if expected == AuthStatus.ANY:
            return self._not_applicable(
                field="authStatus",
                expected=expected.value,
                actual=auth_evaluation.status.value,
                message="Rule accepts any authentication status.",
            )

        if expected == AuthStatus.NOT_APPLICABLE:
            return self._not_applicable(
                field="authStatus",
                expected=expected.value,
                actual=auth_evaluation.status.value,
                message="Authentication is not applicable for this rule.",
            )

        if auth_evaluation.status == AuthStatus.UNKNOWN:
            return self._missing(
                field="authStatus",
                expected=expected.value,
                reason_code=auth_evaluation.reason_code or "MISSING_AUTH_STATUS",
                message=auth_evaluation.message,
            )

        if auth_evaluation.status == expected:
            return self._matched(
                field="authStatus",
                expected=expected.value,
                actual=auth_evaluation.status.value,
                message=auth_evaluation.message,
            )

        return self._not_matched(
            field="authStatus",
            expected=expected.value,
            actual=auth_evaluation.status.value,
            reason_code="AUTH_STATUS_MISMATCH",
            message=auth_evaluation.message,
        )

    def evaluate_clearing_time(
        self,
        transaction: TransactionInput,
        expected: ClearingTimeBand,
    ) -> ClassificationConditionResult:
        clearing_evaluation = self.clearing_time_evaluator.evaluate(transaction)

        if expected == ClearingTimeBand.ANY:
            return self._not_applicable(
                field="clearingTime",
                expected=expected.value,
                actual=clearing_evaluation.band.value,
                message="Rule accepts any clearing time.",
            )

        if clearing_evaluation.band == ClearingTimeBand.UNKNOWN:
            return self._missing(
                field="clearingTime",
                expected=expected.value,
                reason_code=clearing_evaluation.reason_code or "MISSING_CLEARING_TIME",
                message=clearing_evaluation.message,
            )

        if clearing_evaluation.band == expected:
            return self._matched(
                field="clearingTime",
                expected=expected.value,
                actual=clearing_evaluation.band.value,
                message=clearing_evaluation.message,
            )

        return self._not_matched(
            field="clearingTime",
            expected=expected.value,
            actual=clearing_evaluation.band.value,
            reason_code="CLEARING_TIME_MISMATCH",
            message=clearing_evaluation.message,
        )

    def evaluate_card_type(
        self,
        transaction: TransactionInput,
        expected: CardType,
    ) -> ClassificationConditionResult:
        if expected == CardType.ANY:
            return self._not_applicable(
                field="cardType",
                expected=expected.value,
                actual=self._enum_value(transaction.card_type),
                message="Rule accepts any card type.",
            )

        if transaction.card_type is None:
            return self._missing(
                field="cardType",
                expected=expected.value,
                reason_code="MISSING_CARD_TYPE",
            )

        if transaction.card_type == expected:
            return self._matched(
                field="cardType",
                expected=expected.value,
                actual=transaction.card_type.value,
            )

        return self._not_matched(
            field="cardType",
            expected=expected.value,
            actual=transaction.card_type.value,
            reason_code="CARD_TYPE_MISMATCH",
        )

    def evaluate_region(
        self,
        transaction: TransactionInput,
        expected: Region,
    ) -> ClassificationConditionResult:
        if expected == Region.ANY:
            return self._not_applicable(
                field="region",
                expected=expected.value,
                actual=self._actual_region(transaction).value,
                message="Rule accepts any region.",
            )

        actual = self._actual_region(transaction)

        if actual == Region.UNKNOWN:
            return self._missing(
                field="region",
                expected=expected.value,
                reason_code="MISSING_REGION",
            )

        if actual == expected:
            return self._matched(
                field="region",
                expected=expected.value,
                actual=actual.value,
            )

        return self._not_matched(
            field="region",
            expected=expected.value,
            actual=actual.value,
            reason_code="REGION_MISMATCH",
        )

    def evaluate_mcc(
        self,
        transaction: TransactionInput,
        expected: str,
    ) -> ClassificationConditionResult:
        if expected == "Any":
            return self._not_applicable(
                field="mcc",
                expected=expected,
                actual=transaction.mcc,
                message="Rule accepts any MCC.",
            )

        if transaction.mcc is None:
            return self._missing(
                field="mcc",
                expected=expected,
                reason_code="MISSING_MCC",
            )

        if transaction.mcc == expected:
            return self._matched(
                field="mcc",
                expected=expected,
                actual=transaction.mcc,
            )

        return self._not_matched(
            field="mcc",
            expected=expected,
            actual=transaction.mcc,
            reason_code="MCC_MISMATCH",
        )

    def _actual_auth_status(self, transaction: TransactionInput) -> AuthStatus:
        """Derive authentication status using the dedicated 3DS/ECI evaluator."""

        return self.authentication_evaluator.evaluate(transaction).status
    def _actual_clearing_time_band(
        self,
        transaction: TransactionInput,
    ) -> ClearingTimeBand:
        """Derive clearing time band using the dedicated datetime evaluator."""

        return self.clearing_time_evaluator.evaluate(transaction).band
    def _actual_region(self, transaction: TransactionInput) -> Region:
        """Return explicit region or infer a simple EU/Cross-Border value."""

        if transaction.region is not None:
            return transaction.region

        merchant_country = transaction.merchant_country or transaction.country
        issuer_country = transaction.issuer_country

        if merchant_country is None and issuer_country is None:
            logger.info(
                "Missing region data for transaction_id=%s",
                transaction.transaction_id,
            )
            return Region.UNKNOWN

        if merchant_country in EU_COUNTRY_CODES and (
            issuer_country is None or issuer_country in EU_COUNTRY_CODES
        ):
            return Region.EU

        if issuer_country is not None and merchant_country != issuer_country:
            return Region.CROSS_BORDER

        return Region.UNKNOWN

    def _to_datetime(self, value: date | datetime) -> datetime:
        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)

            return value

        return datetime.combine(value, time.min, tzinfo=timezone.utc)

    def _matched(
        self,
        *,
        field: str,
        expected: object,
        actual: object,
        message: str | None = None,
    ) -> ClassificationConditionResult:
        return ClassificationConditionResult(
            field=field,
            expected=expected,
            actual=actual,
            outcome=ConditionOutcome.MATCHED,
            message=message or f"{field} matched.",
        )

    def _not_matched(
        self,
        *,
        field: str,
        expected: object,
        actual: object,
        reason_code: str,
        message: str | None = None,
    ) -> ClassificationConditionResult:
        return ClassificationConditionResult(
            field=field,
            expected=expected,
            actual=actual,
            outcome=ConditionOutcome.NOT_MATCHED,
            reasonCode=reason_code,
            message=message or f"{field} did not match.",
        )

    def _missing(
        self,
        *,
        field: str,
        expected: object,
        reason_code: str,
        message: str | None = None,
    ) -> ClassificationConditionResult:
        return ClassificationConditionResult(
            field=field,
            expected=expected,
            actual=None,
            outcome=ConditionOutcome.MISSING,
            reasonCode=reason_code,
            message=message or f"{field} is missing.",
        )

    def _not_applicable(
        self,
        *,
        field: str,
        expected: object,
        actual: object,
        message: str | None = None,
    ) -> ClassificationConditionResult:
        return ClassificationConditionResult(
            field=field,
            expected=expected,
            actual=actual,
            outcome=ConditionOutcome.NOT_APPLICABLE,
            message=message or f"{field} is not applicable.",
        )

    def _enum_value(self, value: object) -> object:
        if hasattr(value, "value"):
            return value.value

        return value