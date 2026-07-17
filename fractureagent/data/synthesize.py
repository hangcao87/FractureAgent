from __future__ import annotations

import hashlib
import json
from typing import Any, Callable

from fractureagent.schemas import DialogueExample, SourceBlock


def _stable_id(prefix: str, text: str) -> str:
    return f"{prefix}-{hashlib.sha1(text.encode('utf-8')).hexdigest()[:12]}"


def template_dialogue(block: SourceBlock, variant: int = 0) -> DialogueExample:
    patient_styles = [
        "I am unsure whether this is normal and want to progress safely.",
        "I have been doing the home exercises but I am worried about overdoing them.",
        "Can you explain what I should monitor before the next appointment?",
    ]
    user = f"I have a {block.fracture_type} in the {block.body_region}. I am in the {block.phase.replace('_', ' ')} phase. {patient_styles[variant % len(patient_styles)]}"
    assistant = (
        f"The treating clinician's restrictions take priority. Based on the supplied evidence, "
        f"the relevant information for this {block.phase.replace('_', ' ')} phase is: {block.text} "
        "Please stop and contact the clinical team if symptoms are new, worsening, or concerning."
    )
    payload = block.id + str(variant) + user + assistant
    return DialogueExample(
        id=_stable_id("dialogue", payload),
        source_ids=[block.source_id],
        fracture_type=block.fracture_type,
        body_region=block.body_region,
        phase=block.phase,
        messages=[{"role": "user", "content": user}, {"role": "assistant", "content": assistant}],
        metadata={"variant": variant, "generation_mode": "deterministic_template"},
    )


def provider_dialogue(block: SourceBlock, provider: Callable[[str], str], prompt: str, variant: int = 0) -> DialogueExample:
    """Use an external generator only when the user supplies a compliant provider."""
    raw = provider(prompt + "\n\nEvidence block:\n" + block.text)
    value: dict[str, Any] = json.loads(raw)
    if not isinstance(value.get("messages"), list):
        raise ValueError("Provider output must contain a messages list")
    return DialogueExample(
        id=_stable_id("dialogue", block.id + str(variant) + raw),
        source_ids=[block.source_id],
        fracture_type=str(value.get("fracture_type", block.fracture_type)),
        body_region=str(value.get("body_region", block.body_region)),
        phase=str(value.get("phase", block.phase)),
        messages=value["messages"],
        metadata={"variant": variant, "generation_mode": "provider", "provider_output_validated": True},
    )
