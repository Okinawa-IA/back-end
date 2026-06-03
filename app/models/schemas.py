from pydantic import BaseModel
from typing import Any, Dict, Optional


class MoveResponse(BaseModel):
    move: str


class DebugMoveResponse(BaseModel):
    move: str
    received_payload: Optional[Dict[str, Any]] = None