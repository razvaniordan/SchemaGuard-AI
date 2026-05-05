"""Confidence scoring and missing data logging.

Story 2.2.9: Confidence scoring + missing data logging.

The scorer takes a RuleEvaluationResult and produces a bounded confidence
score between 0 and 1.

Rules:
- Base score = matched applicable conditions / applicable conditions.
- Default / Any-only rules receive a lower default base confidence.
- Missing data creates penalties.
- Unknown data creates smaller penalties.
- Final score is capped between 0 and 1.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from models import ConditionOutcome

logger = logging.getLogger(__name__)


DEFAULT_BASE_CONFIDENCE = Decimal("0.50")
MISSING_FIELD_PENALTY = Decimal("0.10")
MAX_MISSING_DATA_PENALTY = Decimal("0.30")
UNKNOWN_DATA_PENALTY = Decimal("0.05")
MAX_UNKNOWN_DATA_PENALTY = Decimal("0.15")
MIN_CONFIDENCE = Decimal("0.00")
MAX_CONFIDENCE = Decimal("1.00")


@dataclass(frozen=True)
class ConfidenceScoreDetails:
    """Detailed confidence scoring output."""

    score: Decimal
    base_score: Decimal
    missing_data_penalty: Decimal
    unknown_data_penalty: Decimal
    matched_count: int
    applicable_count: int
    missing_fields: list[str]
    reason_codes: list[str]


class ConfidenceScorer:
    """Calculate confidence score from rule condition evaluation results."""

    def score(self, rule_evaluation_result) -> ConfidenceScoreDetails:
        """Calculate confidence for one evaluated rule.

        The argument is intentionally duck-typed to avoid circular imports
        with RuleEvaluationResult from condition_evaluator.py.
        """

        base_score = self._base_score(
            matched_count=rule_evaluation_result.matched_count,
            applicable_count=rule_evaluation_result.applicable_count,
        )

        missing_fields = list(dict.fromkeys(rule_evaluation_result.missing_fields))
        reason_codes = list(dict.fromkeys(rule_evaluation_result.reason_codes))

        missing_data_penalty = self._missing_data_penalty(missing_fields)
        unknown_data_penalty = self._unknown_data_penalty(reason_codes)

        final_score = base_score - missing_data_penalty - unknown_data_penalty
        final_score = self._clamp(final_score)
        final_score = self._round(final_score)

        self._log_missing_and_unknown_data(
            rule_evaluation_result=rule_evaluation_result,
            missing_fields=missing_fields,
            reason_codes=reason_codes,
            final_score=final_score,
        )

        return ConfidenceScoreDetails(
            score=final_score,
            base_score=self._round(base_score),
            missing_data_penalty=self._round(missing_data_penalty),
            unknown_data_penalty=self._round(unknown_data_penalty),
            matched_count=rule_evaluation_result.matched_count,
            applicable_count=rule_evaluation_result.applicable_count,
            missing_fields=missing_fields,
            reason_codes=reason_codes,
        )

    def _base_score(
        self,
        *,
        matched_count: int,
        applicable_count: int,
    ) -> Decimal:
        if applicable_count == 0:
            return DEFAULT_BASE_CONFIDENCE

        return Decimal(matched_count) / Decimal(applicable_count)

    def _missing_data_penalty(self, missing_fields: list[str]) -> Decimal:
        penalty = Decimal(len(missing_fields)) * MISSING_FIELD_PENALTY
        return min(penalty, MAX_MISSING_DATA_PENALTY)

    def _unknown_data_penalty(self, reason_codes: list[str]) -> Decimal:
        unknown_reason_codes = [
            reason_code
            for reason_code in reason_codes
            if reason_code.startswith("UNKNOWN_")
        ]

        penalty = Decimal(len(unknown_reason_codes)) * UNKNOWN_DATA_PENALTY
        return min(penalty, MAX_UNKNOWN_DATA_PENALTY)

    def _log_missing_and_unknown_data(
        self,
        *,
        rule_evaluation_result,
        missing_fields: list[str],
        reason_codes: list[str],
        final_score: Decimal,
    ) -> None:
        transaction_id = getattr(rule_evaluation_result, "transaction_id", None)

        rule = getattr(rule_evaluation_result, "rule", None)
        rule_priority = getattr(rule, "priority", None)
        category_code = getattr(rule, "category_code", None)

        if missing_fields:
            logger.info(
                "Missing data during rule evaluation rule_priority=%s category_code=%s "
                "missing_fields=%s reason_codes=%s confidence=%s transaction_id=%s",
                rule_priority,
                category_code,
                missing_fields,
                reason_codes,
                final_score,
                transaction_id,
            )

        unknown_reason_codes = [
            reason_code
            for reason_code in reason_codes
            if reason_code.startswith("UNKNOWN_")
        ]

        if unknown_reason_codes:
            logger.info(
                "Unknown data during rule evaluation rule_priority=%s category_code=%s "
                "unknown_reason_codes=%s confidence=%s transaction_id=%s",
                rule_priority,
                category_code,
                unknown_reason_codes,
                final_score,
                transaction_id,
            )

    def _clamp(self, value: Decimal) -> Decimal:
        return max(MIN_CONFIDENCE, min(MAX_CONFIDENCE, value))

    def _round(self, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)