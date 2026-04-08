"""
FastAPI server exposing the CustomerSupportEnv over HTTP.

Endpoints (OpenEnv spec):
  GET  /              – environment metadata
  GET  /health        – liveness probe
  GET  /tasks         – list available tasks
  POST /reset         – start/reset an episode
  POST /step/{sid}    – take one action
  GET  /state/{sid}   – inspect current state
  DELETE /session/{sid} – clean up session
"""
from __future__ import annotations

import uuid
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import Action, ResetRequest, StepResult, TaskInfo
from environment import CustomerSupportEnv, TASK_CONFIGS

# ---------------------------------------------------------------------------
app = FastAPI(
    title="Customer Support OpenEnv",
    description=(
        "An OpenEnv environment for training and evaluating AI agents on "
        "real-world customer support tasks: ticket classification, routing, "
        "and response drafting."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store  {session_id: CustomerSupportEnv}
_sessions: Dict[str, CustomerSupportEnv] = {}

# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------


def _get_session(session_id: str) -> CustomerSupportEnv:
    env = _sessions.get(session_id)
    if env is None:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return env


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/")
def root():
    return {
        "name": "customer-support-env",
        "version": "1.0.0",
        "description": (
            "OpenEnv environment for customer support ticket management. "
            "Tasks: classify (easy), route (medium), respond (hard)."
        ),
        "tasks": list(TASK_CONFIGS.keys()),
        "spec": "openenv/v1",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks():
    return {
        "tasks": [
            TaskInfo(
                name=name,
                description=cfg["description"].split("\n")[0],
                difficulty=cfg["difficulty"],
                max_steps=cfg["max_steps"],
            ).model_dump()
            for name, cfg in TASK_CONFIGS.items()
        ]
    }


@app.post("/reset")
def reset(request: ResetRequest = None):
    """
    Reset the environment for a given task.
    Returns a session_id and the initial observation.
    """
    if request is None:
        request = ResetRequest()
    env = CustomerSupportEnv()
    try:
        obs = env.reset(task_name=request.task_name, seed=request.seed)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    session_id = str(uuid.uuid4())
    _sessions[session_id] = env

    return {"session_id": session_id, "observation": obs.model_dump()}


@app.post("/step/{session_id}")
def step(session_id: str, action: Action):
    """Take one step in the environment."""
    env = _get_session(session_id)
    if env.done:
        raise HTTPException(
            status_code=400,
            detail="Episode is already done. Call POST /reset to start a new episode.",
        )
    obs, reward, done, info = env.step(action)
    return StepResult(observation=obs, reward=reward, done=done, info=info).model_dump()


@app.get("/state/{session_id}")
def state(session_id: str):
    """Return the current internal state of an episode."""
    env = _get_session(session_id)
    return env.state()


@app.delete("/session/{session_id}")
def close_session(session_id: str):
    """Clean up a session."""
    _get_session(session_id)  # raises 404 if missing
    del _sessions[session_id]
    return {"status": "closed", "session_id": session_id}


# ---------------------------------------------------------------------------
# Dev entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=7860, reload=False)
