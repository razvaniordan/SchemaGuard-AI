from collections import defaultdict
from uuid import uuid4

from core.ml_core import MLCore
from models.analysis_models import (
    AIReportAnomalySummary,
    AIReportRecommendationSummary,
    AIReportRequest,
    AIReportResponse,
    AIReportRootCauseSummary,
    AIReportSummary,
    BulkSimulationRequest,
    BulkSimulationTransactionInput,
)


class AIReportGenerationEngine:
    def __init__(self) -> None:
        # Reuse MLCore so the report is built from the same ML pipeline used by the API.
        self.ml_core = MLCore()

    def generate_report(self, request: AIReportRequest) -> AIReportResponse:
        # Store all transaction-level ML analysis results.
        analysis_results = []

        # Store all rule engine current results for anomaly detection.
        current_results = []

        warnings = []

        for item in request.transactions:
            try:
                result = self.ml_core.analyze_transaction(
                    item.currentResult,
                    item.optimalResult,
                )

                analysis_results.append(result)
                current_results.append(item.currentResult)

            except Exception as error:
                # Report generation should continue even if one transaction fails.
                warnings.append(f"Transaction skipped during report generation: {str(error)}")

        # Generate portfolio-level simulation using the existing bulk simulation engine.
        bulk_result = self.ml_core.simulate_bulk_scenarios(
            BulkSimulationRequest(
                transactions=[
                    BulkSimulationTransactionInput(
                        currentResult=item.currentResult,
                        optimalResult=item.optimalResult,
                    )
                    for item in request.transactions
                ],
                applyTopNRecommendations=2,
            )
        )

        # Detect anomalies across the whole portfolio.
        anomaly_response = self.ml_core.detect_anomalies(current_results)

        # Analyze root causes using all transaction analyses.
        root_cause_response = self.ml_core.analyze_root_causes(analysis_results)

        # Aggregate recommendation-level insights.
        recommendation_summary = self._build_recommendation_summary(analysis_results)

        # Convert anomaly objects into report-friendly objects.
        anomaly_summary = [
            AIReportAnomalySummary(
                transactionId=anomaly.transactionId,
                anomalyType=anomaly.anomalyType,
                severity=anomaly.severity,
                explanation=anomaly.explanation,
            )
            for anomaly in anomaly_response.anomalies
        ]

        # Convert root cause objects into report-friendly objects.
        root_cause_summary = [
            AIReportRootCauseSummary(**cause.model_dump())
            for cause in root_cause_response.rootCauses
        ]

        top_recommendation = (
            recommendation_summary[0].suggestionType
            if recommendation_summary
            else None
        )

        top_root_cause = (
            root_cause_summary[0].condition
            if root_cause_summary
            else None
        )

        summary = AIReportSummary(
            reportName=request.reportName or "AI Optimization Report",
            totalTransactions=len(request.transactions),
            processedTransactions=bulk_result.processedTransactions,
            totalCurrentFees=bulk_result.totalCurrentFees,
            totalOptimizedFees=bulk_result.totalSimulatedFees,
            estimatedSavings=bulk_result.totalSavings,
            anomalyCount=len(anomaly_summary),
            topRecommendation=top_recommendation,
            topRootCause=top_root_cause,
        )

        portfolio_drivers = {
            "savingsByCondition": bulk_result.savingsByCondition,
            "skippedTransactions": [
                item.model_dump()
                for item in bulk_result.skippedTransactions
            ],
            "modelAlgorithmsUsed": list(
                sorted(
                    {
                        result.algorithmUsed
                        for result in analysis_results
                    }
                )
            ),
        }

        return AIReportResponse(
            reportId=str(uuid4()),
            summary=summary,
            recommendationSummary=recommendation_summary,
            anomalySummary=anomaly_summary,
            rootCauseSummary=root_cause_summary,
            portfolioDrivers=portfolio_drivers,
            warnings=warnings + anomaly_response.warnings + root_cause_response.warnings,
        )

    def _build_recommendation_summary(
        self,
        analysis_results,
    ) -> list[AIReportRecommendationSummary]:
        # Aggregate recommendation count, impact, and ranking score by suggestion type.
        grouped = defaultdict(
            lambda: {
                "count": 0,
                "totalImpact": 0.0,
                "totalScore": 0.0,
                "description": "",
            }
        )

        for result in analysis_results:
            for suggestion in result.rankedSuggestions:
                entry = grouped[suggestion.suggestionType]

                entry["count"] += 1
                entry["totalImpact"] += suggestion.expectedImpact
                entry["totalScore"] += suggestion.score
                entry["description"] = suggestion.description

        summaries = []

        for suggestion_type, values in grouped.items():
            count = values["count"]
            total_impact = round(values["totalImpact"], 4)
            average_score = round(values["totalScore"] / count, 4)

            summaries.append(
                AIReportRecommendationSummary(
                    suggestionType=suggestion_type,
                    count=count,
                    totalExpectedImpact=total_impact,
                    averageScore=average_score,
                    priority=self._priority_from_score(average_score),
                    explanation=values["description"],
                )
            )

        # Sort highest-impact recommendations first.
        summaries.sort(
            key=lambda item: item.totalExpectedImpact,
            reverse=True,
        )

        return summaries

    def _priority_from_score(
        self,
        score: float,
    ) -> str:
        # Convert numerical ML/heuristic score into a business-friendly priority label.
        if score >= 0.75:
            return "HIGH"

        if score >= 0.45:
            return "MEDIUM"

        return "LOW"