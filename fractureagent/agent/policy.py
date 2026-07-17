from __future__ import annotations

from typing import Any, Protocol


class Policy(Protocol):
    def generate(self, messages: list[dict[str, str]]) -> str: ...


class DeterministicResearchPolicy:
    """Dependency-free policy for tests and pipeline smoke tests; not a trained model."""

    def generate(self, messages: list[dict[str, str]]) -> str:
        if any(message.get("role") == "tool" for message in messages):
            return "Response: The structured observation has been reviewed. Follow the treating clinician's restrictions, progress gradually only when cleared, and stop for new or worsening symptoms."
        user = messages[-1]["content"].lower()
        if any(term in user for term in ("pain", "numb", "swelling")):
            action = {"tool": "pain_assess", "arguments": {"pain_score": 5, "pain_text": user, "days_since_injury": 0}}
        elif any(term in user for term in ("exercise", "stiff", "move", "movement")):
            action = {"tool": "exercise_query", "arguments": {"fracture_type": "unspecified fracture", "body_region": "unspecified", "phase": "early_mobilization"}}
        else:
            action = {"tool": "progress_track", "arguments": {"phase": "unknown", "weeks_post_injury": 0, "reported_capabilities": []}}
        import json
        return "Thought: select the tool needed for structured research output.\nAction: " + json.dumps(action, sort_keys=True)


class SwiftPolicy:
    """Local inference policy backed by the native ms-swift engine.

    The base model and LoRA adapter must already exist locally. Importing Swift
    lazily keeps deterministic data/evaluation smoke tests dependency-free.
    """

    def __init__(self, model_path: str, adapter_path: str | None = None, **generation_kwargs: Any):
        try:
            from swift import InferRequest, RequestConfig, TransformersEngine
        except ImportError as exc:
            raise RuntimeError("Install the [swift] extra to use SwiftPolicy") from exc
        self._infer_request = InferRequest
        self._request_config = RequestConfig
        engine_kwargs = generation_kwargs.pop("engine_kwargs", {})
        adapters = [adapter_path] if adapter_path else None
        self.engine = TransformersEngine(model_path, adapters=adapters, **engine_kwargs)
        self.generation_kwargs = {"max_tokens": 512, "temperature": 0.0, **generation_kwargs}

    def generate(self, messages: list[dict[str, str]]) -> str:
        request = self._infer_request(messages=messages)
        response = self.engine.infer([request], self._request_config(**self.generation_kwargs))[0]
        return response.choices[0].message.content or ""
