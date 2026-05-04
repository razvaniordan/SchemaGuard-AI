from fastapi import FastAPI

from core.missed_condition_detector import MissedConditionDetector
from models.analysis_models import RuleEngineResult, MissedConditionAnalysis


app = FastAPI(title="SchemeGuard AI ML Service")

detector = MissedConditionDetector()


@app.post("/missed-conditions", response_model=MissedConditionAnalysis)
def analyze_missed_conditions(
    currentResult: RuleEngineResult,
    optimalResult: RuleEngineResult,
):
    return detector.analyze(currentResult, optimalResult)