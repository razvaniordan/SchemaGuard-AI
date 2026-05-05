from core.change_suggestion_engine import ChangeSuggestionEngine
from models.analysis_models import MissedCondition


def test_generates_3ds_and_clearing_suggestions():
    # Create the engine
    engine = ChangeSuggestionEngine()

    # Mock missed conditions from Story 3.1
    missed_conditions = [
        MissedCondition(
            condition="3DS authentication",
            currentValue=False,
            optimalValue=True,
            impact=0.36,
            confidence=0.9,
            explanation="3DS was missing.",
        ),
        MissedCondition(
            condition="clearing time",
            currentValue="2026-05-03",
            optimalValue="2026-05-02",
            impact=0.24,
            confidence=0.9,
            explanation="Clearing was too late.",
        ),
    ]

    # Generate suggestions
    suggestions = engine.generate_suggestions(missed_conditions)

    # Check that two suggestions were generated
    assert len(suggestions) == 2

    # Check that suggestions are sorted by impact
    assert suggestions[0].expectedImpact >= suggestions[1].expectedImpact

    # Check specific suggestion types
    suggestion_types = [suggestion.suggestionType for suggestion in suggestions]

    assert "ENABLE_3DS" in suggestion_types
    assert "REDUCE_CLEARING_TIME" in suggestion_types