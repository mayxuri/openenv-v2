---
title: Customer Support OpenEnv V2
emoji: "🎫"
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
tags:
  - openenv
  - customer-support
  - agentic-evaluation
---

# Customer Support OpenEnv V2

An OpenEnv benchmark for customer support work that is designed to be more interactive, harder to game, and more useful for agent evaluation than the baseline version.

Agents handle three tasks of increasing difficulty:

- `classify`: choose the right support category
- `route`: choose category, priority, and owning team
- `respond`: draft a professional customer reply with realistic next steps

## What Changed in V2

- Ticket pools are larger and cover more realistic support scenarios.
- `ask_clarification` now reveals ticket-specific internal hints instead of returning a generic non-answer.
- The `respond` grader rewards issue acknowledgment, empathy, structure, and actionability.
- The `respond` grader also penalizes unrealistic promises and unsupported claims.

## Why This Environment Is Useful

Customer support is a common operational workflow with clear business value, natural partial credit, and a meaningful difference between shallow pattern matching and real task completion.

This benchmark is intended to test whether an agent can:

- identify the real type of support request
- use an extra step strategically when clarification is valuable
- pick an appropriate priority and owner
- produce a response that sounds helpful without overpromising

## Tasks

| Task | Difficulty | Max Steps | Description |
|------|------------|-----------|-------------|
| `classify` | Easy | 3 | Classify a ticket as billing, technical, account, or general |
| `route` | Medium | 5 | Choose category, priority, and responsible team |
| `respond` | Hard | 5 | Draft a professional support reply with realistic next steps |

### `classify`

Goal: identify the correct ticket category.

Reward:

- `1.0` exact match
- `0.3` adjacent category
- `0.0` wrong category

### `route`

Goal: set category, priority, and team at the same time.

Reward weights:

- category: `0.30`
- priority: `0.40`
- team: `0.30`

Priority gets partial credit when the answer is off by one level.

### `respond`

Goal: write a customer-facing reply that is empathetic, grounded, and operationally realistic.

Deterministic rubric:

- customer name present: `0.15`
- issue acknowledgment: `0.20`
- resolution and next steps: `0.20`
- empathy and professional tone: `0.15`
- actionability and structure: `0.15`
- appropriate length: `0.15`

Additional scoring behavior:

- bonus for must-have task terms
- penalty for unrealistic guarantees or false claims

## Agentic Interaction

The environment exposes `submit` and `ask_clarification`.

Clarification is now meaningful:

- each ticket may reveal one or more internal support hints
- clarification costs a step, so the agent trades off information against efficiency
- the final reward still includes a `0.03` penalty for every extra step before submission

This makes the benchmark more useful for measuring planning and judgment rather than just one-shot classification.

## Observation Space

```json
{
  "ticket": {
    "ticket_id": "T001",
    "subject": "Can't login to my account",
    "body": "...",
    "customer_name": "Alice Johnson",
    "account_type": "pro",
    "created_at": "2024-01-15T10:30:00Z",
    "previous_tickets": []
  },
  "task_name": "classify",
  "task_description": "...",
  "available_action_types": ["submit", "ask_clarification"],
  "step_count": 0,
  "max_steps": 3,
  "feedback": null,
  "cumulative_reward": 0.0
}
```

## Action Space

```json
{
  "action_type": "submit",
  "category": "account",
  "priority": "high",
  "team": "account_team",
  "response_text": "Hello Alice, ...",
  "reasoning": "The issue is account access related."
}
```

| Field | Values | Required for |
|-------|--------|--------------|
| `action_type` | `submit` or `ask_clarification` | always |
| `category` | `billing`, `technical`, `account`, `general` | classify, route |
| `priority` | `low`, `medium`, `high`, `critical` | route |
| `team` | `billing_team`, `technical_team`, `account_team`, `customer_success` | route |
| `response_text` | free text | respond |
| `reasoning` | free text | optional |

## Reward Function

```text
reward = grader_score - (max(0, steps_taken - 1) * 0.03)
reward = clamp(reward, 0.0, 1.0)
```

Properties:

- dense reward with partial credit
- deterministic grading
- explicit incentive for efficient action selection

## Setup

### Run with Docker

```bash
docker build -t customer-support-env-v2 .
docker run -p 7860:7860 customer-support-env-v2
```

### Run locally

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 7860 --reload
```

## API Quick Start

```bash
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task_name": "route", "seed": 42}'

curl -X POST http://localhost:7860/step/<session_id> \
  -H "Content-Type: application/json" \
  -d '{"action_type": "ask_clarification"}'

curl -X POST http://localhost:7860/step/<session_id> \
  -H "Content-Type: application/json" \
  -d '{"action_type": "submit", "category": "technical", "priority": "high", "team": "technical_team"}'
```

## Baseline Script

```bash
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="meta-llama/Llama-3.1-8B-Instruct"
export HF_TOKEN="your-hf-token"
export ENV_BASE_URL="http://localhost:7860"

python inference.py
```

The baseline script works with any OpenAI-compatible API endpoint. Set `API_BASE_URL` and `MODEL_NAME` to match your inference provider.

## Baseline Scores

Evaluated with `meta-llama/Llama-3.1-8B-Instruct` via `https://router.huggingface.co/v1`, seed=42:

| Task | Score | Success | Steps |
|------|-------|---------|-------|
| classify | 1.00 | true | 1 |
| route | 1.00 | true | 1 |
| respond | 1.00 | true | 1 |
| **AVERAGE** | **1.00** | | |

## Project Structure

```text
openenv-customer-support-v2/
|-- app.py
|-- environment.py
|-- models.py
|-- data.py
|-- graders.py
|-- inference.py
|-- openenv.yaml
|-- requirements.txt
|-- Dockerfile
`-- README.md
```

## OpenEnv Compliance

- typed Pydantic models for observations and actions
- `reset`, `step`, and `state` endpoints
- reward always clamped to `[0.0, 1.0]`
- three tasks with easy, medium, and hard difficulty
- deterministic graders
- Dockerized deployment for Hugging Face Spaces

# openenv-v2
