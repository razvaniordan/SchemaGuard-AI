from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class RuleEngineResult(BaseModel):
    category: str
    feeRate: float
    feeAmount: float
    transaction: Dict[str, Any]


class MissedCondition(BaseModel):
    condition: str
    currentValue: Optional[Any]
    optimalValue: Optional[Any]
    impact: float
    confidence: float
    explanation: str


class MissedConditionAnalysis(BaseModel):
    currentCategory: str
    optimalCategory: str
    currentFeeRate: float
    optimalFeeRate: float
    missedConditions: List[MissedCondition]