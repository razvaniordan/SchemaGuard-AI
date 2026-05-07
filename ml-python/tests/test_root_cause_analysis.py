from core.ml_core import MLCore
from models.analysis_models import MissedCondition, MissedConditionAnalysis


def test_root_cause_analysis_ranks_by_score():
    # Create ML core instance
    ml_core = MLCore()
    ml_core.config["models"]["root_cause_driver"]["enabled"] = False
    # Build a small portfolio with repeated missed conditions
    analyses = [
        MissedConditionAnalysis(
            currentCategory="A",
            optimalCategory="B",
            currentFeeRate=2.0,
            optimalFeeRate=1.0,
            missedConditions=[
                MissedCondition(
                    condition="3DS authentication",
                    currentValue=False,
                    optimalValue=True,
                    impact=0.4,
                    confidence=0.9,
                    explanation="Missing 3DS",
                ),
                MissedCondition(
                    condition="clearing time",
                    currentValue="2026-05-03",
                    optimalValue="2026-05-02",
                    impact=0.2,
                    confidence=0.9,
                    explanation="Late clearing",
                ),
            ],
        ),
        MissedConditionAnalysis(
            currentCategory="A",
            optimalCategory="B",
            currentFeeRate=2.0,
            optimalFeeRate=1.0,
            missedConditions=[
                MissedCondition(
                    condition="3DS authentication",
                    currentValue=False,
                    optimalValue=True,
                    impact=0.6,
                    confidence=0.9,
                    explanation="Missing 3DS",
                ),
            ],
        ),
        MissedConditionAnalysis(
            currentCategory="A",
            optimalCategory="B",
            currentFeeRate=2.0,
            optimalFeeRate=1.0,
            missedConditions=[
                MissedCondition(
                    condition="merchant category code",
                    currentValue="5999",
                    optimalValue="5411",
                    impact=0.9,
                    confidence=0.9,
                    explanation="MCC mismatch",
                ),
            ],
        ),
    ]

    # Run root cause analysis
    result = ml_core.analyze_root_causes(analyses)

    # 3DS score = frequency 2 * average impact 0.5 = 1.0
    # MCC score = frequency 1 * average impact 0.9 = 0.9
    assert result.rootCauses[0].condition == "3DS authentication"
    assert result.rootCauses[0].frequency == 2
    assert result.rootCauses[0].totalImpact == 1.0
    assert result.rootCauses[0].averageImpact == 0.5
    assert result.rootCauses[0].score == 1.0

    # Explanation text should be present
    assert result.rootCauses[0].rootCause != ""


def test_root_cause_analysis_marks_low_confidence_for_low_data():
    # Create ML core instance
    ml_core = MLCore()
    ml_core.config["models"]["root_cause_driver"]["enabled"] = False
    # Single occurrence means low confidence
    analyses = [
        MissedConditionAnalysis(
            currentCategory="A",
            optimalCategory="B",
            currentFeeRate=2.0,
            optimalFeeRate=1.0,
            missedConditions=[
                MissedCondition(
                    condition="merchant category code",
                    currentValue="5999",
                    optimalValue="5411",
                    impact=0.9,
                    confidence=0.9,
                    explanation="MCC mismatch",
                ),
            ],
        )
    ]

    # Run root cause analysis
    result = ml_core.analyze_root_causes(analyses)

    assert len(result.rootCauses) == 1
    assert result.rootCauses[0].confidence == "LOW"


def test_root_cause_analysis_handles_empty_input():
    # Create ML core instance
    ml_core = MLCore()
    ml_core.config["models"]["root_cause_driver"]["enabled"] = False
    # Run with no portfolio data
    result = ml_core.analyze_root_causes([])

    assert result.rootCauses == []
    assert len(result.warnings) == 1
    assert result.warnings[0] == "No missed conditions found for root cause analysis."


def test_root_cause_analysis_returns_multiple_causes_for_conflicting_signals():
    # Create ML core instance
    ml_core = MLCore()
    ml_core.config["models"]["root_cause_driver"]["enabled"] = False
    # Two different conditions with equal score should both be returned
    analyses = [
        MissedConditionAnalysis(
            currentCategory="A",
            optimalCategory="B",
            currentFeeRate=2.0,
            optimalFeeRate=1.0,
            missedConditions=[
                MissedCondition(
                    condition="3DS authentication",
                    currentValue=False,
                    optimalValue=True,
                    impact=0.5,
                    confidence=0.9,
                    explanation="Missing 3DS",
                ),
                MissedCondition(
                    condition="clearing time",
                    currentValue="2026-05-03",
                    optimalValue="2026-05-02",
                    impact=0.5,
                    confidence=0.9,
                    explanation="Late clearing",
                ),
            ],
        )
    ]

    # Run root cause analysis
    result = ml_core.analyze_root_causes(analyses)

    conditions = [item.condition for item in result.rootCauses]

    assert "3DS authentication" in conditions
    assert "clearing time" in conditions
    assert len(result.rootCauses) == 2