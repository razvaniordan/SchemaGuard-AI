from core.ml_core import MLCore
from models.analysis_models import MissedCondition, MissedConditionAnalysis

def test_portfolio_pattern_detection_aggregates_correctly():
    # Create ML core instance
    ml_core = MLCore()

    # Prepare mock analyses (simulating multiple transactions)
    analyses = [
        MissedConditionAnalysis(
            currentCategory="A",
            optimalCategory="B",
            currentFeeRate=1.85,
            optimalFeeRate=1.25,
            missedConditions=[
                # Transaction 1 has two issues
                MissedCondition(
                    condition="3DS authentication",
                    currentValue=False,
                    optimalValue=True,
                    impact=0.36,
                    confidence=0.9,
                    explanation="3DS missing",
                ),
                MissedCondition(
                    condition="clearing time",
                    currentValue="2026-05-03",
                    optimalValue="2026-05-02",
                    impact=0.24,
                    confidence=0.9,
                    explanation="Clearing late",
                ),
            ],
        ),
        MissedConditionAnalysis(
            currentCategory="A",
            optimalCategory="B",
            currentFeeRate=1.85,
            optimalFeeRate=1.25,
            missedConditions=[
                # Transaction 2 has only one issue
                MissedCondition(
                    condition="3DS authentication",
                    currentValue=False,
                    optimalValue=True,
                    impact=0.50,
                    confidence=0.9,
                    explanation="3DS missing",
                ),
            ],
        ),
    ]

    # Run portfolio analysis
    result = ml_core.analyze_portfolio(analyses)

    # Validate most common condition
    assert result.mostCommonCondition == "3DS authentication"

    # Validate highest impact condition
    assert result.highestImpactCondition == "3DS authentication"

    # Validate frequency counts
    assert result.conditionFrequency["3DS authentication"] == 2
    assert result.conditionFrequency["clearing time"] == 1

    # Validate average impact calculation
    assert result.averageImpactByCondition["3DS authentication"] == 0.43

    # Validate total savings aggregation
    assert result.totalSavingsOpportunity["3DS authentication"] == 0.86
    assert result.totalSavingsOpportunity["clearing time"] == 0.24


def test_portfolio_pattern_detection_handles_empty_input():
    # Create ML core instance
    ml_core = MLCore()

    # Run with empty dataset
    result = ml_core.analyze_portfolio([])

    # Validate empty response
    assert result.mostCommonCondition is None
    assert result.highestImpactCondition is None
    assert result.conditionFrequency == {}
    assert result.averageImpactByCondition == {}
    assert result.totalSavingsOpportunity == {}