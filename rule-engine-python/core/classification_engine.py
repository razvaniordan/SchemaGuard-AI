"""Transaction classification engine.

Story 2.2.11: REST endpoint integration for POST /classify-transaction.

The engine evaluates rules by priority and returns the first matching
interchange category.
"""

from __future__ import annotations

import logging
from decimal import Decimal

from models import ClassificationResult, TransactionInput
from rules import EU_PHASE_1_RULE_CATALOGUE, PriorityRuleCatalogue

from .condition_evaluator import ConditionEvaluator, RuleEvaluationResult
from .confidence_scorer import ConfidenceScorer

logger = logging.getLogger(__name__)


class ClassificationEngine:
    """Priority-based transaction classification engine."""

    def __init__(
        self,
        *,
        rule_catalogue: PriorityRuleCatalogue = EU_PHASE_1_RULE_CATALOGUE,
        condition_evaluator: ConditionEvaluator | None = None,
        confidence_scorer: ConfidenceScorer | None = None,
    ) -> None:
        self.rule_catalogue = rule_catalogue
        self.condition_evaluator = condition_evaluator or ConditionEvaluator()
        self.confidence_scorer = confidence_scorer or ConfidenceScorer()

    def classify(self, transaction: TransactionInput) -> ClassificationResult:
        """Classify a transaction by evaluating rules in priority order.

        Priority 1 is evaluated first.
        Priority 14 is the default fallback category.
        """

        best_failed_evaluation: RuleEvaluationResult | None = None

        for rule in self.rule_catalogue.iter_by_priority():
            evaluation = self.condition_evaluator.evaluate_rule(
                transaction=transaction,
                rule=rule,
            )

            if evaluation.is_match:
                confidence = self.confidence_scorer.score(evaluation)

                missing_fields = evaluation.missing_fields
                reason_codes = evaluation.reason_codes

                # If only the default fallback rule matched, keep useful diagnostic
                # information from the closest failed rule.
                if (
                    rule.priority == self.rule_catalogue.default_priority
                    and best_failed_evaluation is not None
                ):
                    missing_fields = best_failed_evaluation.missing_fields
                    reason_codes = best_failed_evaluation.reason_codes

                logger.info(
                    "Transaction classified transaction_id=%s rule_priority=%s "
                    "category_code=%s confidence=%s",
                    transaction.transaction_id,
                    rule.priority,
                    rule.category_code,
                    confidence.score,
                )

                return ClassificationResult(
                    transactionId=transaction.transaction_id,
                    category=rule.category,
                    categoryCode=rule.category_code,
                    rulePriority=rule.priority,
                    feeRate=rule.fee_rate,
                    feeRatePercent=rule.fee_rate_percent,
                    feeRateBps=rule.fee_rate_bps,
                    confidence=confidence.score,
                    matchedConditions=evaluation.matched_conditions,
                    missingFields=self._unique(missing_fields),
                    reasonCodes=self._unique(reason_codes),
                    conditionResults=evaluation.condition_results,
                    explanation=(
                        f"Classified as {rule.category.value} "
                        f"using priority {rule.priority}."
                    ),
                )

            best_failed_evaluation = self._select_best_failed_evaluation(
                current_best=best_failed_evaluation,
                candidate=evaluation,
            )

        # Defensive fallback. In normal operation, priority 14 should always match.
        default_rule = self.rule_catalogue.get_default_rule()

        logger.warning(
            "No rule matched transaction_id=%s. Falling back to default category.",
            transaction.transaction_id,
        )

        return ClassificationResult(
            transactionId=transaction.transaction_id,
            category=default_rule.category,
            categoryCode=default_rule.category_code,
            rulePriority=default_rule.priority,
            feeRate=default_rule.fee_rate,
            feeRatePercent=default_rule.fee_rate_percent,
            feeRateBps=default_rule.fee_rate_bps,
            confidence=Decimal("0.00"),
            matchedConditions=[],
            missingFields=[],
            reasonCodes=["NO_MATCHING_RULE"],
            conditionResults=[],
            explanation="No matching rule found. Default category applied.",
        )

    def _select_best_failed_evaluation(
        self,
        *,
        current_best: RuleEvaluationResult | None,
        candidate: RuleEvaluationResult,
    ) -> RuleEvaluationResult:
        if current_best is None:
            return candidate

        if candidate.matched_count > current_best.matched_count:
            return candidate

        if (
            candidate.matched_count == current_best.matched_count
            and candidate.applicable_count > current_best.applicable_count
        ):
            return candidate

        return current_best

    def _unique(self, values: list[str]) -> list[str]:
        return list(dict.fromkeys(values))