from pathlib import Path  # Used to build file paths safely
from typing import Any, Dict, List  # Type hints for better readability

from jinja2 import Environment, FileSystemLoader  # Used for generating explanations

# Import data models (input/output structures)
from models.analysis_models import (
    RuleEngineResult,
    MissedCondition,
    MissedConditionAnalysis,
)


class MissedConditionDetector:
    def __init__(self) -> None:
        # Find the templates folder (../templates relative to this file)
        template_dir = Path(__file__).resolve().parent.parent / "templates"

        # Create Jinja2 environment to load templates
        self.env = Environment(loader=FileSystemLoader(template_dir))

        # Load the explanation template file
        self.template = self.env.get_template("missed_condition_explanation.j2")

    def analyze(
        self,
        current_result: RuleEngineResult,
        optimal_result: RuleEngineResult,
    ) -> MissedConditionAnalysis:
        # List that will store all detected issues
        missed_conditions = []

        # Extract transaction data from both results
        current_tx = current_result.transaction
        optimal_tx = optimal_result.transaction

        # Find differences between current and optimal transaction
        differences = self._diff_transactions(current_tx, optimal_tx)

        # Loop through each changed field
        for field, values in differences.items():
            # Convert field name into a business-friendly condition
            condition = self._identify_condition(field)

            # Skip fields that are not relevant
            if condition is None:
                continue

            # Calculate how much this condition affects the fee difference
            impact = self._calculate_impact(
                current_result.feeRate,
                optimal_result.feeRate,
                field,
            )

            # Calculate how confident we are that this condition matters
            confidence = self._calculate_confidence(field, current_result, optimal_result)

            # Generate a human-readable explanation using template
            explanation = self.template.render(
                condition=condition,
                current_value=values["current"],
                optimal_value=values["optimal"],
                current_category=current_result.category,
                optimal_category=optimal_result.category,
                impact=round(impact, 2),
            )

            # Add this condition to the results list
            missed_conditions.append(
                MissedCondition(
                    condition=condition,
                    currentValue=values["current"],
                    optimalValue=values["optimal"],
                    impact=impact,
                    confidence=confidence,
                    explanation=explanation,
                )
            )

        # Sort conditions by impact (highest first)
        missed_conditions.sort(key=lambda item: item.impact, reverse=True)

        # Return final analysis result
        return MissedConditionAnalysis(
            currentCategory=current_result.category,
            optimalCategory=optimal_result.category,
            currentFeeRate=current_result.feeRate,
            optimalFeeRate=optimal_result.feeRate,
            missedConditions=missed_conditions,
        )

    def _diff_transactions(
        self,
        current_tx: Dict[str, Any],
        optimal_tx: Dict[str, Any],
    ) -> Dict[str, Dict[str, Any]]:
        # Store all differences between current and optimal transaction
        differences = {}

        # Loop through all fields in current transaction
        for field, current_value in current_tx.items():
            # Get corresponding value from optimal transaction
            optimal_value = optimal_tx.get(field)

            # If values are different, record the change
            if current_value != optimal_value:
                differences[field] = {
                    "current": current_value,
                    "optimal": optimal_value,
                }

        return differences

    def _identify_condition(self, field: str) -> str | None:
        # Map technical field names to business meaning
        match field:
            case "threeDS":
                return "3DS authentication"
            case "clearingDate":
                return "clearing time"
            case "authDate":
                return "authorization timing"
            case "mcc":
                return "merchant category code"
            case "channel":
                return "transaction channel"
            case "cardType":
                return "card type"
            case "country":
                return "transaction geography"
            case "currency":
                return "currency"
            case "cardBrand":
                return "card brand"
            case "cardPresence":
                return "card presence"
            case "transactionType":
                return "transaction type"
            case _:
                return None  # Ignore fields that are not important

    def _calculate_impact(
        self,
        current_fee_rate: float,
        optimal_fee_rate: float,
        field: str,
    ) -> float:
        # Calculate total fee difference
        total_difference = max(current_fee_rate - optimal_fee_rate, 0)

        # Define how important each field is
        weight_by_field = {
            "threeDS": 0.6,
            "clearingDate": 0.4,
            "mcc": 0.5,
            "channel": 0.5,
            "cardType": 0.4,
            "country": 0.4,
            "currency": 0.2,
            "cardBrand": 0.2,
            "cardPresence": 0.2,
            "transactionType": 0.2,
        }

        # Get weight (default to small value if unknown field)
        weight = weight_by_field.get(field, 0.1)

        # Return weighted impact
        return round(total_difference * weight, 4)

    def _calculate_confidence(
        self,
        field: str,
        current_result: RuleEngineResult,
        optimal_result: RuleEngineResult,
    ) -> float:
        # If categories are the same, confidence is low
        if current_result.category == optimal_result.category:
            return 0.3

        # Fields we are very confident about
        high_confidence_fields = {"threeDS", "clearingDate", "mcc", "channel", "cardType"}

        # If field is important, return high confidence
        if field in high_confidence_fields:
            return 0.9

        # Otherwise medium confidence
        return 0.6