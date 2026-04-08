"""
Deterministic graders for each task.
All graders return (reward: float in [0,1], info: dict).
"""
from __future__ import annotations

from typing import Dict, Any, Tuple, Iterable

PRIORITY_LEVELS = ["low", "medium", "high", "critical"]


def _count_hits(candidates: Iterable[str], text: str) -> int:
    return sum(1 for candidate in candidates if candidate in text)


def _sentence_count(text: str) -> int:
    return sum(text.count(punctuation) for punctuation in ".!?")


def grade_classify(action: Dict[str, Any], answer: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """
    Task 1 - Classify: reward = 1.0 for correct category, 0.0 otherwise.
    Partial credit (0.3) if submission is an adjacent, semantically related category.
    """
    submitted = (action.get("category") or "").lower().strip()
    correct = answer["category"]

    adjacent: Dict[str, set] = {
        "billing": {"general"},
        "general": {"billing", "account"},
        "account": {"general", "technical"},
        "technical": {"account"},
    }

    if submitted == correct:
        reward = 1.0
        verdict = "correct"
    elif submitted in adjacent.get(correct, set()):
        reward = 0.3
        verdict = "adjacent"
    else:
        reward = 0.0
        verdict = "wrong"

    info = {
        "verdict": verdict,
        "submitted_category": submitted,
        "expected_category": correct,
    }
    return reward, info


def grade_route(action: Dict[str, Any], answer: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """
    Task 2 - Route: weighted score across three dimensions.
      category  -> 30%
      priority  -> 40%  (adjacent priority gets 50% credit)
      team      -> 30%
    """
    submitted_cat = (action.get("category") or "").lower().strip()
    submitted_pri = (action.get("priority") or "").lower().strip()
    submitted_team = (action.get("team") or "").lower().strip()

    correct_cat = answer["category"]
    correct_pri = answer["priority"]
    correct_team = answer["team"]

    cat_score = 1.0 if submitted_cat == correct_cat else 0.0

    if submitted_pri == correct_pri:
        pri_score = 1.0
    elif submitted_pri in PRIORITY_LEVELS and correct_pri in PRIORITY_LEVELS:
        diff = abs(PRIORITY_LEVELS.index(submitted_pri) - PRIORITY_LEVELS.index(correct_pri))
        pri_score = 0.5 if diff == 1 else 0.0
    else:
        pri_score = 0.0

    team_score = 1.0 if submitted_team == correct_team else 0.0

    reward = round(cat_score * 0.30 + pri_score * 0.40 + team_score * 0.30, 4)

    info = {
        "category_score": cat_score,
        "priority_score": pri_score,
        "team_score": team_score,
        "total_reward": reward,
        "submitted": {
            "category": submitted_cat,
            "priority": submitted_pri,
            "team": submitted_team,
        },
        "expected": {
            "category": correct_cat,
            "priority": correct_pri,
            "team": correct_team,
        },
    }
    return reward, info


def grade_respond(
    action: Dict[str, Any],
    answer: Dict[str, Any],
    ticket: Dict[str, Any],
) -> Tuple[float, Dict[str, Any]]:
    """
    Task 3 - Respond: deterministic rubric scoring.

    Rubric (sums to 1.0):
      - Customer name present            : 0.15
      - Issue acknowledgement            : 0.20
      - Resolution and next steps        : 0.20
      - Empathy and professional tone    : 0.15
      - Actionability / structure        : 0.15
      - Appropriate length               : 0.15

    A penalty is applied for unrealistic overpromises or obviously unsafe claims.
    """
    response_text = (action.get("response_text") or "").strip()
    response_lower = response_text.lower()

    if not response_text:
        return 0.0, {"error": "No response_text provided"}

    breakdown: Dict[str, float] = {}

    customer_words = ticket["customer_name"].lower().split()
    name_hit = any(word in response_lower for word in customer_words)
    breakdown["name_mentioned"] = 0.15 if name_hit else 0.0

    issue_terms = list(answer.get("issue_keywords", [])) + list(answer.get("must_include_words", []))
    issue_hits = _count_hits(issue_terms, response_lower)
    issue_denominator = max(1, len(issue_terms))
    breakdown["issue_acknowledged"] = round(0.20 * min(1.0, issue_hits / issue_denominator), 4)

    resolution_phrases = answer.get("resolution_phrases", [])
    resolution_hits = _count_hits(resolution_phrases, response_lower)
    resolution_denominator = max(1, len(resolution_phrases))
    breakdown["resolution_provided"] = round(
        0.20 * min(1.0, resolution_hits / max(2, resolution_denominator * 0.6)),
        4,
    )

    empathy_phrases = answer.get("empathy_phrases", [])
    empathy_hits = _count_hits(empathy_phrases, response_lower)
    tone_bonus = 1.0 if any(greeting in response_lower for greeting in ["hi ", "hello ", "dear "]) else 0.5
    breakdown["empathetic_tone"] = round(
        0.15 * min(1.0, max(empathy_hits / max(1, len(empathy_phrases)), tone_bonus)),
        4,
    )

    action_phrases = answer.get("action_phrases", [])
    action_hits = _count_hits(action_phrases, response_lower)
    sentence_count = _sentence_count(response_text)
    actionable_fraction = action_hits / max(1, len(action_phrases))
    structure_fraction = min(1.0, sentence_count / 3)
    breakdown["actionable_next_steps"] = round(
        0.15 * min(1.0, max(actionable_fraction, structure_fraction * 0.7)),
        4,
    )

    word_count = len(response_text.split())
    min_w = answer.get("min_words", 60)
    max_w = answer.get("max_words", 500)
    if min_w <= word_count <= max_w:
        length_score = 0.15
    elif word_count < min_w:
        length_score = round(0.15 * (word_count / min_w), 4)
    else:
        length_score = round(0.15 * max(0.0, 1.0 - (word_count - max_w) / max_w), 4)
    breakdown["length_appropriate"] = length_score

    must_words = answer.get("must_include_words", [])
    must_hits = _count_hits(must_words, response_lower)
    must_word_bonus = round(0.10 * (must_hits / max(1, len(must_words))), 4)

    forbidden_hits = _count_hits(answer.get("forbidden_phrases", []), response_lower)
    guarantee_hits = _count_hits(
        ["guarantee", "definitely fixed", "resolved now", "certainly complete"],
        response_lower,
    )
    penalty = round(min(0.20, forbidden_hits * 0.10 + guarantee_hits * 0.05), 4)

    total = round(sum(breakdown.values()) + must_word_bonus - penalty, 4)
    total = min(1.0, max(0.0, total))

    return total, {
        "total_reward": total,
        "breakdown": breakdown,
        "must_word_bonus": must_word_bonus,
        "penalty": penalty,
        "word_count": word_count,
        "sentence_count": sentence_count,
    }
