"""
OpenEnv Customer Support - Pydantic Models
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal


class TicketInfo(BaseModel):
    ticket_id: str
    subject: str
    body: str
    customer_name: str
    account_type: Literal["free", "pro", "enterprise"]
    created_at: str
    previous_tickets: List[Dict[str, Any]] = Field(default_factory=list)


class Observation(BaseModel):
    ticket: TicketInfo
    task_name: str
    task_description: str
    available_action_types: List[str]
    step_count: int
    max_steps: int
    feedback: Optional[str] = None
    cumulative_reward: float = 0.0


class Action(BaseModel):
    action_type: str = Field(
        ...,
        description="One of: submit, ask_clarification",
    )
    category: Optional[str] = Field(
        None,
        description="Ticket category: billing | technical | account | general",
    )
    priority: Optional[str] = Field(
        None,
        description="Ticket priority: low | medium | high | critical",
    )
    team: Optional[str] = Field(
        None,
        description="Team assignment: billing_team | technical_team | account_team | customer_success",
    )
    response_text: Optional[str] = Field(
        None,
        description="Full drafted response to send to the customer (task: respond)",
    )
    reasoning: Optional[str] = Field(
        None,
        description="Agent's step-by-step reasoning",
    )


class Reward(BaseModel):
    reward: float = Field(ge=0.0, le=1.0)
    done: bool
    info: Dict[str, Any] = Field(default_factory=dict)


class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any] = Field(default_factory=dict)


class ResetRequest(BaseModel):
    task_name: str = Field("classify", description="One of: classify | route | respond")
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")


class TaskInfo(BaseModel):
    name: str
    description: str
    difficulty: str
    max_steps: int
