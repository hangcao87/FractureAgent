"""Verifiable, deterministic reward functions for GRPO.

Each function follows the TRL GRPOTrainer signature
    fn(prompts, completions, **dataset_columns) -> list[float]
and returns one reward in [0, 1] per completion. The dataset columns
(`gold_tool`, `gold_escalate`, `rubric`) come from data/processed/grpo_prompts.jsonl.
Rewards are intentionally rule-based and reproducible — no judge model — so the RL
signal is auditable. Combine them with the weights in configs/grpo.yaml."""
from __future__ import annotations
import json, re, yaml
from ..agent.react import parse_action
from ..agent.safety_gate import escalate, detect_complications

_BLOCKS = ("Thought:", "Action:", "Response:")

def _text(c):  # TRL passes completions as strings or [{"content":...}]
    return c if isinstance(c, str) else c[-1]["content"]

def format_reward(prompts, completions, **kw):
    """1.0 if Thought/Action/Response present in order and Action is valid JSON/DONE."""
    out = []
    for c in completions:
        t = _text(c); ok = all(b in t for b in _BLOCKS)
        order = t.find("Thought:") < t.find("Action:") < t.find("Response:")
        act = parse_action(t)
        valid = act is not None and act[0] != "__malformed__"
        out.append(1.0 if (ok and order and valid) else 0.0)
    return out

def tool_choice_reward(prompts, completions, gold_tool=None, **kw):
    gold_tool = gold_tool or [None] * len(completions)
    out = []
    for c, g in zip(completions, gold_tool):
        act = parse_action(_text(c))
        chosen = act[0] if act else None
        out.append(1.0 if (g is not None and chosen == g) else 0.0)
    return out

def safety_reward(prompts, completions, gold_escalate=None, **kw):
    """Reward correct escalate/withhold. The user utterance is parsed from the prompt."""
    gold_escalate = gold_escalate or [False] * len(completions)
    out = []
    for p, c, g in zip(prompts, completions, gold_escalate):
        user = (p.split("User:")[-1].strip() if "User:" in p else p)
        gate, _ = escalate(user, None, None, None, None)
        gold = bool(g) or gate or bool(detect_complications(user))
        t = _text(c).lower()
        said = ("escalat" in t or "contact your" in t or "urgent" in t or "seek" in t)
        out.append(1.0 if said == gold else 0.0)
    return out

def task_completion_reward(prompts, completions, rubric=None, **kw):
    """Coarse rubric: correct tool used AND (if required) escalation surfaced."""
    rubric = rubric or [{}] * len(completions)
    tc = tool_choice_reward(prompts, completions, gold_tool=[r.get("must_use_tool") for r in rubric])
    sf = safety_reward(prompts, completions, gold_escalate=[r.get("must_escalate", False) for r in rubric])
    return [0.5 * a + 0.5 * b for a, b in zip(tc, sf)]

def make_weighted_reward(cfg_path="configs/grpo.yaml"):
    w = yaml.safe_load(open(cfg_path))["reward_weights"]
    fns = {"format": format_reward, "tool_choice": tool_choice_reward,
           "safety": safety_reward, "task_completion": task_completion_reward}
    def weighted(prompts, completions, **kw):
        total = [0.0] * len(completions)
        for name, fn in fns.items():
            r = fn(prompts, completions, **kw)
            total = [t + w[name] * ri for t, ri in zip(total, r)]
        return total
    weighted.__name__ = "weighted_reward"
    return weighted

# TRL can take a list of reward fns; expose the individual ones too.
REWARD_FUNCS = [format_reward, tool_choice_reward, safety_reward, task_completion_reward]
