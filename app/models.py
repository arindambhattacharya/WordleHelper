from pydantic import BaseModel, Field
from typing import List, Literal

FeedbackType = Literal["gray", "yellow", "green"]

class GuessEntry(BaseModel):
    word: str = Field(..., min_length=5, max_length=5, pattern="^[a-zA-Z]+$")
    feedback: List[FeedbackType] = Field(..., min_items=5, max_items=5)

class BoardState(BaseModel):
    guesses: List[GuessEntry]

class Suggestion(BaseModel):
    word: str
    entropy: float
    is_solution: bool

class SuggestionsResponse(BaseModel):
    solutions: List[Suggestion]
    info_gain: List[Suggestion]
