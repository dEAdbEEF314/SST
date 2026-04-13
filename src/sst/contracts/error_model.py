from pydantic import BaseModel
from typing import Literal

class ErrorModel(BaseModel):
    type: Literal["RETRYABLE", "NON_RETRYABLE", "LOGIC_FAILURE"]
    message: str
    retry_count: int = 0
