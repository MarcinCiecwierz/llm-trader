from pydantic import BaseModel, Field
from enum import Enum

class Decision(str, Enum):
    HOLD = "hold"
    BUY = "buy"
    SELL = "sell"

class ModelResponse(BaseModel):
    answer: str
    decision: Decision
