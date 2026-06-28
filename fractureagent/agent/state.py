"""Persistent patient-state record and its deterministic update (Eq. 3).
s_{t+1} = update(s_t, u_t, y_t, o_t) — a pure function, so multi-turn
trajectories are reproducible from logs."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any

PHASES = ["acute_immobilization", "early_mobilization", "strengthening", "return_to_activity"]

@dataclass
class PatientState:
    fracture_type: str = "unknown"
    location: str = "unknown"
    operative: bool | None = None
    days_since_injury: int = 0
    phase: str = "acute_immobilization"
    nrs_history: list[int] = field(default_factory=list)
    rom: dict[str, float] = field(default_factory=dict)   # self-reported / clinician goniometry
    completed_sessions: int = 0
    complication_flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]: return asdict(self)

def update(s: PatientState, user_utt: str, reply: str, obs: dict | None) -> PatientState:
    """Refresh state from the new turn. Deterministic in (s, user_utt, reply, obs)."""
    obs = obs or {}
    if "nrs" in obs and obs["nrs"] is not None:
        s.nrs_history = s.nrs_history + [int(obs["nrs"])]
    if "rom" in obs and isinstance(obs["rom"], dict):
        s.rom = {**s.rom, **obs["rom"]}
    if obs.get("session_completed"):
        s.completed_sessions += 1
    for flag in obs.get("complication_flags", []):
        if flag not in s.complication_flags:
            s.complication_flags.append(flag)
    if "phase" in obs and obs["phase"] in PHASES:
        s.phase = obs["phase"]
    return s
