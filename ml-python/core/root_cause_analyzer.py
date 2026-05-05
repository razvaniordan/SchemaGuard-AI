from typing import Any, Dict, List

import pandas as pd

from models.analysis_models import (
    MissedConditionAnalysis,
    RootCauseAnalysisResponse,
    RootCauseItem,
)


class RootCauseAnalyzer:
    def analyze(
        self,
        analyses: List[Any],
    ) -> RootCauseAnalysisResponse:
        """
        Analyze portfolio-level missed conditions and identify likely root causes.

        The method combines:
        - frequency of each missed condition
        - average financial impact
        - total financial impact

        The final score is:
        score = frequency * averageImpact
        """

        rows = []
        warnings = []

        # Convert all input analyses into flat rows.
        # Supports direct MissedConditionAnalysis objects and objects with an .analysis field.
        for item in analyses:
            analysis = item.analysis if hasattr(item, "analysis") else item

            # Skip invalid objects instead of failing the full portfolio analysis.
            if not hasattr(analysis, "missedConditions"):
                warnings.append("One portfolio item was skipped because it does not contain missed conditions.")
                continue

            for condition in analysis.missedConditions:
                rows.append(
                    {
                        "condition": condition.condition,
                        "impact": condition.impact,
                    }
                )

        # Empty input or no missed conditions means no root causes can be inferred.
        if not rows:
            return RootCauseAnalysisResponse(
                rootCauses=[],
                warnings=["No missed conditions found for root cause analysis."],
            )

        # Use pandas for portfolio-level aggregation.
        df = pd.DataFrame(rows)

        # Group by condition and calculate frequency, total impact, and average impact.
        grouped = (
            df.groupby("condition")
            .agg(
                frequency=("condition", "count"),
                totalImpact=("impact", "sum"),
                averageImpact=("impact", "mean"),
            )
            .reset_index()
        )

        # Ranking formula from the acceptance criteria.
        grouped["score"] = grouped["frequency"] * grouped["averageImpact"]

        # Sort highest root-cause score first.
        grouped = grouped.sort_values(
            by="score",
            ascending=False,
        )

        root_causes = []

        for _, row in grouped.iterrows():
            condition = row["condition"]
            frequency = int(row["frequency"])
            total_impact = round(float(row["totalImpact"]), 4)
            average_impact = round(float(row["averageImpact"]), 4)
            score = round(float(row["score"]), 4)

            root_causes.append(
                RootCauseItem(
                    condition=condition,
                    frequency=frequency,
                    totalImpact=total_impact,
                    averageImpact=average_impact,
                    score=score,
                    confidence=self._calculate_confidence(frequency),
                    rootCause=self._build_root_cause_explanation(condition),
                )
            )

        return RootCauseAnalysisResponse(
            rootCauses=root_causes,
            warnings=warnings,
        )

    def _calculate_confidence(
        self,
        frequency: int,
    ) -> str:
        """
        Estimate confidence based on how much supporting evidence exists.

        Low data volume should be marked LOW.
        """

        if frequency < 3:
            return "LOW"

        if frequency < 10:
            return "MEDIUM"

        return "HIGH"

    def _build_root_cause_explanation(
        self,
        condition: str,
    ) -> str:
        """
        Convert a missed condition into a likely business/root cause explanation.
        """

        explanations: Dict[str, str] = {
            "3DS authentication": (
                "3DS may not be consistently enforced in the checkout or authentication flow."
            ),
            "clearing time": (
                "Clearing may be delayed by settlement processing, acquirer configuration, or operational timing."
            ),
            "merchant category code": (
                "Merchant category code classification may be incorrect or not aligned with preferred interchange rules."
            ),
            "transaction channel": (
                "Transactions may be classified under the wrong channel, affecting interchange eligibility."
            ),
            "card type": (
                "Card type classification may be inconsistent, causing transactions to miss better fee categories."
            ),
            "transaction geography": (
                "Country or region classification may be driving less favorable interchange treatment."
            ),
            "currency": (
                "Currency handling may be contributing to missed optimization opportunities."
            ),
            "card brand": (
                "Card brand-specific routing or classification may be affecting fee optimization."
            ),
            "card presence": (
                "Card-present versus card-not-present classification may be inconsistent."
            ),
            "transaction type": (
                "Transaction type classification may be preventing access to better interchange categories."
            ),
        }

        return explanations.get(
            condition,
            "This condition appears repeatedly and should be reviewed as a potential systemic optimization issue.",
        )