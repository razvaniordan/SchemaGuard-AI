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

class ChangeSuggestion(BaseModel):
    # Short name of the suggested change
    suggestionType: str

    # Clear action the user should take
    action: str

    # Field that should be changed, for example "threeDS"
    field: str

    # Current value from the transaction
    currentValue: Optional[Any]

    # Recommended new value
    suggestedValue: Optional[Any]

    # Expected financial impact
    expectedImpact: float

    # How hard it is to apply this change
    difficulty: str

    # Human-readable explanation
    description: str


class ChangeSuggestionResponse(BaseModel):
    # List of suggestions sorted by financial impact
    suggestions: List[ChangeSuggestion]