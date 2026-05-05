from typing import List

from models.analysis_models import ChangeSuggestion, MissedCondition


class ChangeSuggestionEngine:
    def generate_suggestions(
        self,
        missed_conditions: List[MissedCondition],
    ) -> List[ChangeSuggestion]:
        # This list will store all generated suggestions
        suggestions = []

        # Loop through each missed condition detected by Story 3.1
        for condition in missed_conditions:
            # Generate a suggestion depending on the missed condition type
            suggestion = self._create_suggestion(condition)

            # If a valid suggestion was created, add it to the list
            if suggestion is not None:
                suggestions.append(suggestion)

        # Remove suggestions that conflict with each other
        suggestions = self._resolve_conflicts(suggestions)

        # Validate suggestions against basic business rules
        suggestions = self._validate_business_rules(suggestions)

        # Sort suggestions by expected financial impact, highest first
        suggestions.sort(key=lambda item: item.expectedImpact, reverse=True)

        return suggestions

    def _create_suggestion(
        self,
        condition: MissedCondition,
    ) -> ChangeSuggestion | None:
        # Decide which suggestion to create based on the condition name
        match condition.condition:
            case "3DS authentication":
                return ChangeSuggestion(
                    suggestionType="ENABLE_3DS",
                    action="Enable 3DS authentication",
                    field="threeDS",
                    currentValue=condition.currentValue,
                    suggestedValue=True,
                    expectedImpact=condition.impact,
                    difficulty="Medium",
                    description=(
                        "Enable 3DS authentication to move eligible eCommerce "
                        "transactions into a secure interchange category."
                    ),
                )

            case "clearing time":
                return ChangeSuggestion(
                    suggestionType="REDUCE_CLEARING_TIME",
                    action="Reduce clearing time to 24 hours or less",
                    field="clearingDate",
                    currentValue=condition.currentValue,
                    suggestedValue=condition.optimalValue,
                    expectedImpact=condition.impact,
                    difficulty="Hard",
                    description=(
                        "Reduce the time between authorization and clearing so the "
                        "transaction can qualify for preferred interchange rates."
                    ),
                )

            case "merchant category code":
                return ChangeSuggestion(
                    suggestionType="FIX_MCC",
                    action="Review and correct merchant category code",
                    field="mcc",
                    currentValue=condition.currentValue,
                    suggestedValue=condition.optimalValue,
                    expectedImpact=condition.impact,
                    difficulty="Medium",
                    description=(
                        "Correcting the MCC may allow the transaction to qualify "
                        "for a preferred category such as grocery or regulated MCC."
                    ),
                )

            case "transaction channel":
                return ChangeSuggestion(
                    suggestionType="REVIEW_CHANNEL",
                    action="Review transaction channel classification",
                    field="channel",
                    currentValue=condition.currentValue,
                    suggestedValue=condition.optimalValue,
                    expectedImpact=condition.impact,
                    difficulty="Hard",
                    description=(
                        "The transaction channel affects interchange classification. "
                        "Review whether the transaction was classified correctly."
                    ),
                )

            case "card type":
                return ChangeSuggestion(
                    suggestionType="REVIEW_CARD_TYPE",
                    action="Review card type classification",
                    field="cardType",
                    currentValue=condition.currentValue,
                    suggestedValue=condition.optimalValue,
                    expectedImpact=condition.impact,
                    difficulty="Hard",
                    description=(
                        "Card type strongly affects interchange fees. Review whether "
                        "the transaction was classified as debit, credit, prepaid, or commercial correctly."
                    ),
                )

            case _:
                # If the condition is not supported yet, do not generate a suggestion
                return None

    def _resolve_conflicts(
        self,
        suggestions: List[ChangeSuggestion],
    ) -> List[ChangeSuggestion]:
        # Store one suggestion per field to avoid duplicate/conflicting suggestions
        best_suggestion_by_field = {}

        for suggestion in suggestions:
            existing = best_suggestion_by_field.get(suggestion.field)

            # If no suggestion exists for this field, keep this one
            if existing is None:
                best_suggestion_by_field[suggestion.field] = suggestion
                continue

            # If there is already a suggestion for this field,
            # keep the one with the higher expected impact
            if suggestion.expectedImpact > existing.expectedImpact:
                best_suggestion_by_field[suggestion.field] = suggestion

        return list(best_suggestion_by_field.values())

    def _validate_business_rules(
        self,
        suggestions: List[ChangeSuggestion],
    ) -> List[ChangeSuggestion]:
        # Store only valid suggestions
        valid_suggestions = []

        for suggestion in suggestions:
            # Rule: expected impact must be positive
            if suggestion.expectedImpact <= 0:
                continue

            # Rule: suggested value should not be the same as current value
            if suggestion.currentValue == suggestion.suggestedValue:
                continue

            # Rule: difficulty must be one of the supported values
            if suggestion.difficulty not in {"Easy", "Medium", "Hard"}:
                continue

            valid_suggestions.append(suggestion)

        return valid_suggestions