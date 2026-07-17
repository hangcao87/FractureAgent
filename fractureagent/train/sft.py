from __future__ import annotations

from pathlib import Path
from typing import Any

from fractureagent.data.io import read_jsonl
from fractureagent.train.format import to_chat_records


def train_qlora(model_path: str, dataset_path: str, output_dir: str, config: dict[str, Any]) -> None:
    """Run supervised QLoRA training using only a user-provided local base model."""
    if not model_path or "${" in model_path:
        raise ValueError("Provide MODEL_PATH or --model-path pointing to a local base model")
    model_dir = Path(model_path)
    if not model_dir.exists():
        raise FileNotFoundError(f"Local base model not found: {model_dir}")
    try:
        import torch
        from datasets import Dataset
        from peft import LoraConfig
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
        from trl import SFTTrainer
    except ImportError as exc:
        raise RuntimeError("Install the [train] extras before running QLoRA training") from exc

    records = to_chat_records(read_jsonl(dataset_path), float(config.get("agent_trace_ratio", 0.7)), int(config.get("seed", 2026)))
    tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    dataset = Dataset.from_list(records)

    def render(row: dict[str, Any]) -> dict[str, str]:
        text = tokenizer.apply_chat_template(row["messages"], tokenize=False, add_generation_prompt=False)
        return {"text": text}

    dataset = dataset.map(render, remove_columns=dataset.column_names)
    bits = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)
    model = AutoModelForCausalLM.from_pretrained(model_dir, quantization_config=bits, device_map="auto", local_files_only=True)
    lora_cfg = config.get("lora", {})
    peft_cfg = LoraConfig(
        r=int(lora_cfg.get("r", 16)), lora_alpha=int(lora_cfg.get("alpha", 32)), lora_dropout=float(lora_cfg.get("dropout", 0.05)),
        target_modules=list(lora_cfg.get("target_modules", ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"])), task_type="CAUSAL_LM",
    )
    args = TrainingArguments(
        output_dir=output_dir, num_train_epochs=float(config.get("num_train_epochs", 4)), learning_rate=float(config.get("learning_rate", 2e-4)),
        per_device_train_batch_size=int(config.get("per_device_train_batch_size", 1)), gradient_accumulation_steps=int(config.get("gradient_accumulation_steps", 32)),
        warmup_ratio=float(config.get("warmup_ratio", 0.03)), logging_steps=int(config.get("logging_steps", 10)), save_steps=int(config.get("save_steps", 250)),
        gradient_checkpointing=bool(config.get("gradient_checkpointing", True)), bf16=bool(config.get("bf16", True)), report_to="none", seed=int(config.get("seed", 2026)),
    )
    trainer = SFTTrainer(model=model, tokenizer=tokenizer, train_dataset=dataset, peft_config=peft_cfg, args=args, dataset_text_field="text", max_seq_length=int(config.get("max_seq_length", 4096)))
    trainer.train()
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
