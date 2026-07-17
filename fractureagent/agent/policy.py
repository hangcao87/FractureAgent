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


class TransformersPolicy:
    """Optional local Hugging Face policy. It loads only a user-supplied local path."""

    def __init__(self, model_path: str, adapter_path: str | None = None, **generation_kwargs: Any):
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:
            raise RuntimeError("Install the [train] extras to use TransformersPolicy") from exc
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True, device_map="auto", **generation_kwargs.pop("model_kwargs", {}))
        if adapter_path:
            from peft import PeftModel
            self.model = PeftModel.from_pretrained(self.model, adapter_path, local_files_only=True)
        self.generation_kwargs = {"max_new_tokens": 512, "do_sample": False, **generation_kwargs}

    def generate(self, messages: list[dict[str, str]]) -> str:
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        output = self.model.generate(**inputs, **self.generation_kwargs)
        return self.tokenizer.decode(output[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True)
