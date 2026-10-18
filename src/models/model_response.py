from enum import Enum

from pydantic import BaseModel


class Decision(str, Enum):
    HOLD = "hold"
    BUY = "buy"
    SELL = "sell"


class ModelResponse(BaseModel):
    answer: str
    decision: Decision
