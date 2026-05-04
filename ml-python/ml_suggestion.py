from pydantic import BaseModel


class MLSuggestion(BaseModel):
    suggestionType: str
    impact: str
    difficulty: str
    description: str