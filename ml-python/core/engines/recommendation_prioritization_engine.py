from typing import List

from core.ml_core import MLCore
from models.analysis_models import (
    PrioritizedRecommendation,
    RecommendationPrioritizationRequest,
    RecommendationPrioritizationResponse,
)


class RecommendationPrioritizationEngine:
    def __init__(self) -> None:
        # MLCore already contains missed-condition detection,
        # suggestion generation, heuristic ranking, and ML ranking.
        self.ml_core = MLCore()

    def prioritize(
        self,
        request: RecommendationPrioritizationRequest,
    ) -> RecommendationPrioritizationResponse:
        # Run the existing ML pipeline.
        analysis_result = self.ml_core.analyze_transaction(
            request.currentResult,
            request.optimalResult,
        )

        recommendations = []

        for suggestion in analysis_result.rankedSuggestions:
            recommendations.append(
                PrioritizedRecommendation(
                    suggestionType=suggestion.suggestionType,
                    action=suggestion.action,
                    field=suggestion.field,
                    currentValue=suggestion.currentValue,
                    suggestedValue=suggestion.suggestedValue,
                    expectedImpact=suggestion.expectedImpact,
                    difficulty=suggestion.difficulty,
                    description=suggestion.description,
                    score=suggestion.score,
                    priority=self._priority_from_score(suggestion.score),
                    rankingReason=self._build_ranking_reason(
                        suggestion.score,
                        suggestion.expectedImpact,
                        suggestion.difficulty,
                    ),
                )
            )

        return RecommendationPrioritizationResponse(
            recommendations=recommendations,
            algorithmUsed=analysis_result.algorithmUsed,
            modelVersion=self._infer_model_version(analysis_result.algorithmUsed),
            fallbackUsed="heuristic_ranking" in analysis_result.algorithmUsed,
            warnings=[],
        )

    def _priority_from_score(self, score: float) -> str:
        # Convert numerical ranking score into business-friendly priority.
        if score >= 0.75:
            return "HIGH"

        if score >= 0.45:
            return "MEDIUM"

        return "LOW"

    def _build_ranking_reason(
        self,
        score: float,
        expected_impact: float,
        difficulty: str,
    ) -> str:
        # Explain why this recommendation received its priority.
        return (
            f"Recommendation ranked with score {score}. "
            f"Expected impact is {expected_impact}, "
            f"implementation difficulty is {difficulty}."
        )

    def _infer_model_version(
        self,
        algorithm_used: str,
    ) -> str | None:
        # Expose model version only when ML ranking was used.
        if "ml_ranking" in algorithm_used:
            return "ranking-model-v1"

        return None