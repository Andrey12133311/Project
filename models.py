from __future__ import annotations
from typing import Any, Dict, List, Literal
from pydantic import BaseModel, Field

class ProcessRequest(BaseModel):
    text: str = Field(min_length=3)
    source: str = "web"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentStep(BaseModel):
    name: str
    status: Literal["ok", "warning", "needs_human"]
    summary: str
    data: Dict[str, Any] = Field(default_factory=dict)

class ProcessResult(BaseModel):
    run_id: str
    category: str
    priority: Literal["low", "normal", "high", "critical"]
    confidence: float
    route_to: str
    extracted: Dict[str, Any]
    risks: List[str]
    suggested_actions: List[str]
    draft_reply: str
    human_approval_required: bool
    steps: List[AgentStep]
