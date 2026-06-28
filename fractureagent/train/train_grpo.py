"""GRPO reinforcement fine-tuning on top of the SFT policy.

GRPO (Shao et al., 2024) samples G completions per prompt and computes group-relative
advantages — no separate value model. We use TRL's GRPOTrainer with the deterministic,
verifiable rewards in fractureagent/rewards/rewards.py (format + tool-choice + safety +
task-completion). KL to the reference (SFT) policy is controlled by `beta`.

Run: python -m fractureagent.train.train_grpo --config configs/grpo.yaml
"""
import argparse, yaml, torch
from datasets import load_dataset
from transformers import AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig
from trl import GRPOTrainer, GRPOConfig
from ..rewards.rewards import REWARD_FUNCS

def main(config):
    cfg = yaml.safe_load(open(config)); g = cfg["grpo"]
    tok = AutoTokenizer.from_pretrained(cfg["model_name"])
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    ds = load_dataset("json", data_files={"train": cfg["data"]["prompt_file"]})["train"]
    q = cfg["quantization"]
    bnb = BitsAndBytesConfig(load_in_4bit=q["load_in_4bit"],
        bnb_4bit_quant_type=q["bnb_4bit_quant_type"],
        bnb_4bit_compute_dtype=getattr(torch, q["bnb_4bit_compute_dtype"]))
    lc = cfg["lora"]
    peft_cfg = LoraConfig(r=lc["r"], lora_alpha=lc["lora_alpha"], lora_dropout=lc["lora_dropout"],
                          target_modules=lc["target_modules"], task_type=lc["task_type"])
    args = GRPOConfig(output_dir=cfg["output_dir"], num_generations=g["num_generations"],
        max_prompt_length=g["max_prompt_length"], max_completion_length=g["max_completion_length"],
        temperature=g["temperature"], learning_rate=g["learning_rate"], beta=g["beta"],
        num_train_epochs=g["num_train_epochs"], per_device_train_batch_size=g["per_device_train_batch_size"],
        gradient_accumulation_steps=g["gradient_accumulation_steps"], bf16=True, report_to="none")
    trainer = GRPOTrainer(model=cfg["model_name"], reward_funcs=REWARD_FUNCS, args=args,
                          train_dataset=ds, peft_config=peft_cfg,
                          model_init_kwargs={"quantization_config": bnb, "torch_dtype": torch.bfloat16})
    trainer.train()
    trainer.save_model(cfg["output_dir"])
    print(f"[train_grpo] GRPO policy saved -> {cfg['output_dir']}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--config", default="configs/grpo.yaml")
    main(ap.parse_args().config)
