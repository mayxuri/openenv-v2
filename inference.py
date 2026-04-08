"""
Inference Script — Customer Support OpenEnv Baseline
=====================================================

MANDATORY environment variables:
  API_BASE_URL      The API endpoint for the LLM  (default: https://api.openai.com/v1)
  MODEL_NAME        The model identifier           (default: gpt-4o-mini)
  HF_TOKEN          Your Hugging Face / API key    (used as the OpenAI API key)
  LOCAL_IMAGE_NAME  Docker image name for local env (default: customer-support-env)
  ENV_BASE_URL      Running environment URL        (default: http://localhost:7860)

STDOUT FORMAT (strictly followed for evaluation):
  [START] task=<task> env=<benchmark> model=<model>
  [STEP]  step=<n> action=<str> reward=<0.00> done=<true|false> error=<str|null>
  [END]   success=<true|false> steps=<n> score=<score> rewards=<rewards>
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import requests
from openai import OpenAI

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_BASE_URL: str = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME: str = os.getenv("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")
HF_TOKEN: str = os.getenv("HF_TOKEN", os.getenv("OPENAI_API_KEY", ""))
LOCAL_IMAGE_NAME: str = os.getenv("LOCAL_IMAGE_NAME", "customer-support-env")
ENV_BASE_URL: str = os.getenv("ENV_BASE_URL", "http://localhost:7860")

BENCHMARK = "customer-support-openenv"
TASKS = ["classify", "route", "respond"]
SEED = 42
ENV_READY_TIMEOUT = 60  # seconds

client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)

# ---------------------------------------------------------------------------
# Environment HTTP helpers
# ---------------------------------------------------------------------------


def _call(method: str, path: str, body: Optional[Dict] = None, timeout: int = 30) -> Dict:
    url = f"{ENV_BASE_URL}{path}"
    if method == "GET":
        r = requests.get(url, timeout=timeout)
    elif method == "POST":
        r = requests.post(url, json=body, timeout=timeout)
    elif method == "DELETE":
        r = requests.delete(url, timeout=timeout)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")
    r.raise_for_status()
    return r.json()


def wait_for_env(timeout: int = ENV_READY_TIMEOUT) -> bool:
    """Poll /health until the environment server is ready."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = requests.get(f"{ENV_BASE_URL}/health", timeout=5)
            if resp.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(2)
    return False


def maybe_start_docker() -> Optional[subprocess.Popen]:
    """
    If the env server is not reachable and LOCAL_IMAGE_NAME is set,
    start a local Docker container and return the process handle.
    """
    try:
        requests.get(f"{ENV_BASE_URL}/health", timeout=3)
        return None  # already running
    except Exception:
        pass

    if not LOCAL_IMAGE_NAME:
        return None

    print(f"Starting local Docker container from image '{LOCAL_IMAGE_NAME}' ...", flush=True)
    proc = subprocess.Popen(
        ["docker", "run", "--rm", "-p", "7860:7860", LOCAL_IMAGE_NAME],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return proc


# ---------------------------------------------------------------------------
# LLM agent
# ---------------------------------------------------------------------------

SYSTEM_PROMPTS = {
    "classify": (
        "You are a customer support triage agent. Your job is to classify a support ticket "
        "into exactly one of these categories:\n"
        "  billing   – payment, invoice, refund, pricing issues\n"
        "  technical – bugs, errors, crashes, slow performance\n"
        "  account   – login, password, 2FA, email, profile issues\n"
        "  general   – how-to questions, feature requests, feedback\n\n"
        "Respond with a JSON object containing:\n"
        "  action_type: 'submit'\n"
        "  category: one of billing | technical | account | general\n"
        "  reasoning: brief explanation\n"
        "Output ONLY valid JSON."
    ),
    "route": (
        "You are a customer support routing agent. Analyse the ticket and respond with:\n"
        "  action_type: 'submit'\n"
        "  category: billing | technical | account | general\n"
        "  priority: low | medium | high | critical\n"
        "    (critical=production down/revenue loss, high=major breakage, "
        "medium=partial issue, low=question)\n"
        "  team: billing_team | technical_team | account_team | customer_success\n"
        "  reasoning: brief explanation\n"
        "Output ONLY valid JSON."
    ),
    "respond": (
        "You are a professional customer support agent. Draft a response to the ticket.\n"
        "Requirements:\n"
        "  • Address the customer by first name\n"
        "  • Apologise for the inconvenience\n"
        "  • Acknowledge the specific issue\n"
        "  • Provide concrete next steps or a resolution\n"
        "  • Keep it 80–350 words, professional and warm\n\n"
        "Respond with a JSON object containing:\n"
        "  action_type: 'submit'\n"
        "  response_text: your full response (plain text, no markdown)\n"
        "  reasoning: one-line explanation of your approach\n"
        "Output ONLY valid JSON."
    ),
}


def get_agent_action(task_name: str, observation: Dict) -> Tuple[Dict, str]:
    """Ask the LLM for the next action given the current observation."""
    ticket = observation["ticket"]
    prev = json.dumps(ticket.get("previous_tickets", []))

    user_content = (
        f"=== Customer Ticket ===\n"
        f"ID:       {ticket['ticket_id']}\n"
        f"Subject:  {ticket['subject']}\n"
        f"Customer: {ticket['customer_name']} ({ticket['account_type']} plan)\n"
        f"Body:\n{ticket['body']}\n"
        f"Previous tickets: {prev}\n\n"
        f"Step {observation['step_count']+1}/{observation['max_steps']}\n"
    )
    if observation.get("feedback"):
        user_content += f"Last feedback: {observation['feedback']}\n"
    user_content += "\nDecide your action:"

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[task_name]},
            {"role": "user", "content": user_content},
        ],
        temperature=0.0,
        max_tokens=1024,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    action = json.loads(raw)
    if "action_type" not in action:
        action["action_type"] = "submit"

    # Compact action string for [STEP] log line
    action_str = json.dumps({k: v for k, v in action.items() if k != "response_text"})
    if len(action_str) > 120:
        action_str = action_str[:117] + "..."

    return action, action_str


# ---------------------------------------------------------------------------
# Episode runner
# ---------------------------------------------------------------------------


def run_episode(task_name: str) -> Dict[str, Any]:
    """Run one full episode and return results."""
    total_rewards: List[float] = []
    step_count = 0
    score = 0.0
    success = False
    last_error: Optional[str] = None

    # Reset
    reset_resp = _call("POST", "/reset", {"task_name": task_name, "seed": SEED})
    session_id: str = reset_resp["session_id"]
    observation: Dict = reset_resp["observation"]

    print(
        f"[START] task={task_name} env={BENCHMARK} model={MODEL_NAME}",
        flush=True,
    )

    try:
        while step_count < observation["max_steps"]:
            try:
                action, action_str = get_agent_action(task_name, observation)
            except Exception as exc:
                last_error = str(exc)
                action = {"action_type": "submit", "reasoning": "fallback"}
                action_str = "fallback-action"

            try:
                step_resp = _call("POST", f"/step/{session_id}", action)
            except Exception as exc:
                last_error = str(exc)
                break

            reward: float = step_resp["reward"]
            done: bool = step_resp["done"]
            observation = step_resp["observation"]
            step_count += 1
            total_rewards.append(reward)

            error_field = last_error if last_error else "null"
            print(
                f"[STEP] step={step_count} action={action_str} "
                f"reward={reward:.2f} done={'true' if done else 'false'} "
                f"error={error_field}",
                flush=True,
            )

            if done:
                score = reward
                success = score >= 0.5
                break

    except Exception as exc:
        last_error = str(exc)

    finally:
        try:
            _call("DELETE", f"/session/{session_id}")
        except Exception:
            pass

    rewards_str = ",".join(f"{r:.2f}" for r in total_rewards)
    print(
        f"[END] success={'true' if success else 'false'} steps={step_count} "
        f"score={score:.2f} rewards={rewards_str}",
        flush=True,
    )

    return {
        "task": task_name,
        "score": score,
        "steps": step_count,
        "success": success,
        "rewards": total_rewards,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    docker_proc = maybe_start_docker()

    print(f"Waiting for environment at {ENV_BASE_URL} ...", flush=True)
    if not wait_for_env():
        print("ERROR: Environment did not become ready in time.", flush=True)
        if docker_proc:
            docker_proc.terminate()
        sys.exit(1)

    print(
        f"Environment ready. Running baseline: model={MODEL_NAME}  tasks={TASKS}",
        flush=True,
    )

    results = []
    for task_name in TASKS:
        try:
            result = run_episode(task_name)
        except Exception as exc:
            print(f"ERROR in task {task_name}: {exc}", flush=True)
            result = {
                "task": task_name,
                "score": 0.0,
                "steps": 0,
                "success": False,
                "rewards": [],
            }
        results.append(result)

    # Summary
    avg_score = sum(r["score"] for r in results) / len(results)
    print("\n=== BASELINE RESULTS ===", flush=True)
    for r in results:
        print(
            f"  {r['task']:10s}  score={r['score']:.2f}  "
            f"success={str(r['success']).lower()}  steps={r['steps']}",
            flush=True,
        )
    print(f"  {'AVERAGE':10s}  score={avg_score:.2f}", flush=True)

    if docker_proc:
        docker_proc.terminate()


if __name__ == "__main__":
    main()
