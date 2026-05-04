from fastapi import FastAPI

from core.missed_condition_detector import MissedConditionDetector
from core.change_suggestion_engine import ChangeSuggestionEngine
from models.analysis_models import (
    RuleEngineResult,
    MissedConditionAnalysis,
    ChangeSuggestionResponse,
)


app = FastAPI(title="SchemeGuard AI ML Service")

# Create service instances
detector = MissedConditionDetector()
suggestion_engine = ChangeSuggestionEngine()


@app.post("/missed-conditions", response_model=MissedConditionAnalysis)
def analyze_missed_conditions(
    currentResult: RuleEngineResult,
    optimalResult: RuleEngineResult,
):
    # Compare current and optimal result
    return detector.analyze(currentResult, optimalResult)


@app.post("/change-suggestions", response_model=ChangeSuggestionResponse)
def generate_change_suggestions(
    currentResult: RuleEngineResult,
    optimalResult: RuleEngineResult,
):
    # First detect missed conditions
    analysis = detector.analyze(currentResult, optimalResult)

    # Then convert missed conditions into actionable suggestions
    suggestions = suggestion_engine.generate_suggestions(analysis.missedConditions)

    # Return sorted suggestions
    return ChangeSuggestionResponse(suggestions=suggestions)