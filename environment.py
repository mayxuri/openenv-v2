"""
CustomerSupportEnv - core environment class implementing the OpenEnv interface.

Three tasks of increasing difficulty:
  classify  (easy)   -> identify ticket category
  route     (medium) -> classify + set priority + assign team
  respond   (hard)   -> draft a complete customer response
"""
from __future__ import annotations

import random
from typing import Optional, Tuple, Dict, Any, List

from models import Observation, Action, TicketInfo
from data import get_ticket_for_task
from graders import grade_classify, grade_route, grade_respond


TASK_CONFIGS: Dict[str, Dict[str, Any]] = {
    "classify": {
        "description": (
            "Classify the incoming customer support ticket into exactly one category.\n"
            "Valid categories: billing | technical | account | general\n"
            "  billing   - payment issues, invoices, refunds, pricing\n"
            "  technical - bugs, errors, crashes, performance problems\n"
            "  account   - login, password, profile, 2FA, email changes\n"
            "  general   - how-to questions, feature requests, feedback\n"
            "You may use ask_clarification once or twice to reveal an internal triage note before submitting.\n"
            "Submit with action_type='submit' and the 'category' field set."
        ),
        "difficulty": "easy",
        "max_steps": 3,
        "available_action_types": ["submit", "ask_clarification"],
    },
    "route": {
        "description": (
            "Route the ticket by determining three things:\n"
            "  1. category : billing | technical | account | general\n"
            "  2. priority : low | medium | high | critical\n"
            "  3. team     : billing_team | technical_team | account_team | customer_success\n"
            "Priority guidelines:\n"
            "  critical - production down, revenue impact, data loss\n"
            "  high     - significant feature broken, workaround hard, enterprise customer\n"
            "  medium   - partial degradation, workaround exists\n"
            "  low      - general questions, cosmetic issues\n"
            "You may use ask_clarification to reveal one internal routing hint before submitting.\n"
            "Submit with action_type='submit' and all three fields set."
        ),
        "difficulty": "medium",
        "max_steps": 5,
        "available_action_types": ["submit", "ask_clarification"],
    },
    "respond": {
        "description": (
            "Draft a professional, empathetic customer support response for the ticket.\n"
            "Your response must:\n"
            "  - Address the customer by name\n"
            "  - Acknowledge their specific issue\n"
            "  - Apologize for the inconvenience when appropriate\n"
            "  - Provide concrete next steps or a realistic resolution\n"
            "  - Maintain a professional, warm tone\n"
            "  - Avoid making promises the support team cannot guarantee\n"
            "  - Be between 60-500 words unless the task allows more\n"
            "You may use ask_clarification to reveal one internal support note before submitting.\n"
            "Submit with action_type='submit' and the 'response_text' field set."
        ),
        "difficulty": "hard",
        "max_steps": 5,
        "available_action_types": ["submit", "ask_clarification"],
    },
}


class CustomerSupportEnv:
    """OpenEnv-compliant environment for customer support ticket management."""

    def __init__(self) -> None:
        self.task_name: Optional[str] = None
        self.current_ticket: Optional[TicketInfo] = None
        self._current_answer: Optional[Dict[str, Any]] = None
        self._ticket_raw: Optional[Dict[str, Any]] = None
        self._clarification_queue: List[str] = []
        self._clarifications_used: int = 0
        self.step_count: int = 0
        self.cumulative_reward: float = 0.0
        self.done: bool = False
        self.seed: int = 42

    def reset(self, task_name: str, seed: Optional[int] = None) -> Observation:
        """Start a new episode. Returns the initial observation."""
        if task_name not in TASK_CONFIGS:
            raise ValueError(
                f"Unknown task '{task_name}'. Available: {list(TASK_CONFIGS.keys())}"
            )

        self.task_name = task_name
        self.step_count = 0
        self.cumulative_reward = 0.0
        self.done = False
        self.seed = seed if seed is not None else random.randint(0, 9999)
        self._clarifications_used = 0

        ticket_data = get_ticket_for_task(task_name, self.seed)
        self._ticket_raw = ticket_data
        self._current_answer = ticket_data["answer"]
        self._clarification_queue = list(ticket_data.get("clarifications", []))

        self.current_ticket = TicketInfo(
            ticket_id=ticket_data["ticket_id"],
            subject=ticket_data["subject"],
            body=ticket_data["body"],
            customer_name=ticket_data["customer_name"],
            account_type=ticket_data["account_type"],
            created_at=ticket_data["created_at"],
            previous_tickets=ticket_data.get("previous_tickets", []),
        )

        return self._make_observation(feedback=None)

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        """
        Apply action and return (observation, reward, done, info).
        Reward is always in [0.0, 1.0].
        """
        if self.done:
            raise RuntimeError("Episode has ended. Call reset() to start a new episode.")

        config = TASK_CONFIGS[self.task_name]
        self.step_count += 1
        reward = 0.0
        info: Dict[str, Any] = {}
        feedback: Optional[str] = None
        done = False

        action_type = (action.action_type or "").lower().strip()

        if action_type == "ask_clarification":
            reward = 0.0
            self._clarifications_used += 1
            if self._clarification_queue:
                clue = self._clarification_queue.pop(0)
                feedback = (
                    f"Clarification {self._clarifications_used}: {clue} "
                    "Use this hint to refine your next action."
                )
                info = {
                    "clarification_revealed": True,
                    "clarifications_remaining": len(self._clarification_queue),
                }
            else:
                feedback = (
                    "No additional clarification is available. "
                    "Use the ticket details and prior hints to decide your next step."
                )
                info = {
                    "clarification_revealed": False,
                    "clarifications_remaining": 0,
                }

        elif action_type == "submit":
            action_dict = action.model_dump()

            if self.task_name == "classify":
                raw_reward, info = grade_classify(action_dict, self._current_answer)
            elif self.task_name == "route":
                raw_reward, info = grade_route(action_dict, self._current_answer)
            elif self.task_name == "respond":
                raw_reward, info = grade_respond(
                    action_dict,
                    self._current_answer,
                    self._ticket_raw,
                )
            else:
                raw_reward = 0.0

            step_penalty = max(0, self.step_count - 1) * 0.03
            reward = round(max(0.0, min(1.0, raw_reward - step_penalty)), 4)
            done = True
            feedback = (
                f"Graded. Raw score: {raw_reward:.2f}  "
                f"Step penalty: {step_penalty:.2f}  Final: {reward:.2f}"
            )

        else:
            reward = 0.0
            feedback = (
                f"Unrecognized action_type '{action_type}'. "
                f"Use one of: {config['available_action_types']}"
            )

        if self.step_count >= config["max_steps"] and not done:
            done = True
            feedback = (feedback or "") + " [Max steps reached - episode ended with score 0.]"

        self.cumulative_reward = round(self.cumulative_reward + reward, 4)
        self.done = done

        return self._make_observation(feedback=feedback), reward, done, info

    def state(self) -> Dict[str, Any]:
        """Return the current environment state (for inspection/debugging)."""
        return {
            "task_name": self.task_name,
            "ticket_id": self.current_ticket.ticket_id if self.current_ticket else None,
            "step_count": self.step_count,
            "max_steps": TASK_CONFIGS[self.task_name]["max_steps"] if self.task_name else None,
            "cumulative_reward": self.cumulative_reward,
            "done": self.done,
            "seed": self.seed,
            "clarifications_used": self._clarifications_used,
            "clarifications_remaining": len(self._clarification_queue),
        }

    def _make_observation(self, feedback: Optional[str]) -> Observation:
        config = TASK_CONFIGS[self.task_name]
        return Observation(
            ticket=self.current_ticket,
            task_name=self.task_name,
            task_description=config["description"],
            available_action_types=config["available_action_types"],
            step_count=self.step_count,
            max_steps=config["max_steps"],
            feedback=feedback,
            cumulative_reward=self.cumulative_reward,
        )
