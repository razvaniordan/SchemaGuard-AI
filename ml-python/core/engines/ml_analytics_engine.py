from collections import defaultdict

from core.ml_core import MLCore
from models.analysis_models import (
    AnomalyTrendItem,
    MLAnalyticsRequest,
    MLAnalyticsResponse,
    MLConfidenceMetric,
    RecommendationSuccessMetric,
    RootCauseDriverMetric,
    TransactionDrilldownItem,
)


class MLAnalyticsEngine:
    def __init__(self) -> None:
        # Reuse MLCore so analytics are based on the same ML pipeline as the API.
        self.ml_core = MLCore()

    def analyze_portfolio(
        self,
        request: MLAnalyticsRequest,
    ) -> MLAnalyticsResponse:
        analysis_results = []
        current_results = []
        warnings = []

        # Run full ML analysis for every transaction pair.
        for item in request.transactions:
            try:
                result = self.ml_core.analyze_transaction(
                    item.currentResult,
                    item.optimalResult,
                )

                analysis_results.append(result)
                current_results.append(item.currentResult)

            except Exception as error:
                # Analytics should continue even if one transaction fails.
                warnings.append(f"Transaction skipped in analytics: {str(error)}")

        # Detect anomalies across the portfolio.
        anomaly_response = self.ml_core.detect_anomalies(current_results)

        # Analyze systemic root causes across all analyses.
        root_cause_response = self.ml_core.analyze_root_causes(analysis_results)

        anomaly_trends = self._build_anomaly_trends(anomaly_response.anomalies)

        recommendation_metrics = self._build_recommendation_success_metrics(
            analysis_results
        )

        root_cause_drivers = self._build_root_cause_drivers(
            root_cause_response.rootCauses
        )

        confidence_metrics = self._build_confidence_metrics(analysis_results)

        drilldown = self._build_transaction_drilldown(
            analysis_results=analysis_results,
            current_results=current_results,
            anomalies=anomaly_response.anomalies,
            root_causes=root_cause_response.rootCauses,
        )

        portfolio_opportunities = {
            metric.suggestionType: metric.totalExpectedImpact
            for metric in recommendation_metrics
        }

        return MLAnalyticsResponse(
            totalTransactions=len(request.transactions),
            anomalyTrends=anomaly_trends,
            recommendationSuccessMetrics=recommendation_metrics,
            rootCauseDrivers=root_cause_drivers,
            portfolioOptimizationOpportunities=portfolio_opportunities,
            mlConfidenceAnalytics=confidence_metrics,
            transactionDrilldown=drilldown,
            warnings=warnings + anomaly_response.warnings + root_cause_response.warnings,
        )

    def _build_anomaly_trends(
        self,
        anomalies,
    ) -> list[AnomalyTrendItem]:
        # Group anomalies by anomaly type.
        grouped = defaultdict(
            lambda: {
                "count": 0,
                "highSeverityCount": 0,
            }
        )

        for anomaly in anomalies:
            entry = grouped[anomaly.anomalyType]
            entry["count"] += 1

            if anomaly.severity == "HIGH":
                entry["highSeverityCount"] += 1

        return [
            AnomalyTrendItem(
                anomalyType=anomaly_type,
                count=values["count"],
                highSeverityCount=values["highSeverityCount"],
            )
            for anomaly_type, values in grouped.items()
        ]

    def _build_recommendation_success_metrics(
        self,
        analysis_results,
    ) -> list[RecommendationSuccessMetric]:
        # Aggregate recommendation counts, scores, and impacts by suggestion type.
        grouped = defaultdict(
            lambda: {
                "count": 0,
                "scoreSum": 0.0,
                "impactSum": 0.0,
            }
        )

        for result in analysis_results:
            for suggestion in result.rankedSuggestions:
                entry = grouped[suggestion.suggestionType]
                entry["count"] += 1
                entry["scoreSum"] += suggestion.score
                entry["impactSum"] += suggestion.expectedImpact

        metrics = []

        for suggestion_type, values in grouped.items():
            count = values["count"]
            average_score = round(values["scoreSum"] / count, 4)

            # Use average ranking score as a proxy for estimated recommendation success.
            estimated_success_rate = round(min(max(average_score, 0.0), 1.0), 4)

            metrics.append(
                RecommendationSuccessMetric(
                    suggestionType=suggestion_type,
                    count=count,
                    averageScore=average_score,
                    totalExpectedImpact=round(values["impactSum"], 4),
                    estimatedSuccessRate=estimated_success_rate,
                )
            )

        metrics.sort(
            key=lambda item: item.totalExpectedImpact,
            reverse=True,
        )

        return metrics

    def _build_root_cause_drivers(
        self,
        root_causes,
    ) -> list[RootCauseDriverMetric]:
        # Convert root-cause output into analytics-friendly metrics.
        drivers = []

        for cause in root_causes:
            drivers.append(
                RootCauseDriverMetric(
                    condition=cause.condition,
                    frequency=cause.frequency,
                    totalImpact=cause.totalImpact,
                    averageImpact=cause.averageImpact,
                    combinedScore=getattr(cause, "combinedScore", None),
                    mlDriverScore=getattr(cause, "mlDriverScore", None),
                    modelVersion=getattr(cause, "modelVersion", None),
                )
            )

        drivers.sort(
            key=lambda item: item.combinedScore or item.totalImpact,
            reverse=True,
        )

        return drivers

    def _build_confidence_metrics(
        self,
        analysis_results,
    ) -> list[MLConfidenceMetric]:
        # Count which algorithm combinations were used.
        grouped = defaultdict(int)

        for result in analysis_results:
            grouped[result.algorithmUsed] += 1

        return [
            MLConfidenceMetric(
                algorithmUsed=algorithm,
                count=count,
            )
            for algorithm, count in grouped.items()
        ]

    def _build_transaction_drilldown(
        self,
        analysis_results,
        current_results,
        anomalies,
        root_causes,
    ) -> list[TransactionDrilldownItem]:
        # Map anomaly labels by transaction ID for drill-down view.
        anomalies_by_transaction = defaultdict(list)

        for anomaly in anomalies:
            anomalies_by_transaction[anomaly.transactionId].append(
                anomaly.anomalyType
            )

        top_root_cause = root_causes[0].condition if root_causes else None

        items = []

        for result, current in zip(analysis_results, current_results):
            transaction_id = current.transaction.get(
                "transactionId",
                current.transaction.get("id"),
            )

            items.append(
                TransactionDrilldownItem(
                    transactionId=transaction_id,
                    category=current.category,
                    feeAmount=current.feeAmount,
                    recommendations=[
                        suggestion.suggestionType
                        for suggestion in result.rankedSuggestions
                    ],
                    anomalies=anomalies_by_transaction.get(transaction_id, []),
                    topRootCause=top_root_cause,
                )
            )

        return items