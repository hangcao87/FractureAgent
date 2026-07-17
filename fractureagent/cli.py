from __future__ import annotations

import argparse
import json
from pathlib import Path

from fractureagent.agent.policy import DeterministicResearchPolicy, TransformersPolicy
from fractureagent.agent.react import ReActAgent
from fractureagent.agent.tools import ToolRegistry
from fractureagent.config import load_yaml
from fractureagent.data.build import build_dataset
from fractureagent.data.io import read_jsonl
from fractureagent.eval.run import evaluate


def _json(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def make_agent(args, deterministic: bool = False):
    cfg = load_yaml(args.agent_config)
    policy = DeterministicResearchPolicy() if deterministic else TransformersPolicy(args.model_path, adapter_path=args.adapter_path)
    tool_schemas = _json(cfg["tool_schemas"])
    evidence = read_jsonl(args.evidence) if getattr(args, "evidence", None) else []
    return ReActAgent(policy, Path(cfg["system_prompt"]).read_text(encoding="utf-8"), tool_schemas, ToolRegistry(evidence), Path(cfg["escalation_response"]).read_text(encoding="utf-8"), int(cfg.get("max_steps", 4)))


def main() -> None:
    parser = argparse.ArgumentParser(prog="fractureagent")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("build-dataset")
    p.add_argument("--config", required=True); p.add_argument("--input", required=True); p.add_argument("--output", required=True)
    p = sub.add_parser("run-agent")
    p.add_argument("--agent-config", default="configs/agent.yaml"); p.add_argument("--user", required=True); p.add_argument("--evidence"); p.add_argument("--deterministic", action="store_true"); p.add_argument("--model-path"); p.add_argument("--adapter-path")
    p = sub.add_parser("evaluate")
    p.add_argument("--agent-config", default="configs/agent.yaml"); p.add_argument("--scenarios", required=True); p.add_argument("--evidence"); p.add_argument("--deterministic", action="store_true"); p.add_argument("--model-path"); p.add_argument("--adapter-path"); p.add_argument("--output")
    p = sub.add_parser("train-sft")
    p.add_argument("--config", required=True); p.add_argument("--model-path", required=True); p.add_argument("--dataset", required=True); p.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    if args.command == "build-dataset":
        print(json.dumps(build_dataset(args.input, args.output, load_yaml(args.config)), ensure_ascii=False, indent=2))
    elif args.command == "train-sft":
        from fractureagent.train.sft import train_qlora
        train_qlora(args.model_path, args.dataset, args.output_dir, load_yaml(args.config))
    elif args.command == "run-agent":
        result = make_agent(args, deterministic=args.deterministic).run(args.user)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        result = evaluate(make_agent(args, deterministic=args.deterministic), args.scenarios)
        output = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).write_text(output + "\n", encoding="utf-8")
        print(output)


if __name__ == "__main__":
    main()
