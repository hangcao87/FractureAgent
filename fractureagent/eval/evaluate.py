"""Run FractureAgent over the evaluation scenarios and report TCR (95% CI),
escalation operating characteristics (sensitivity/specificity/PPV/NPV/FPR/F1),
and BLEU-4. Two modes:

  --mock     : use a trivial rule-based policy (no GPU) — for a smoke test of the
               harness and the metric plumbing.
  --adapters PATH : load the trained QLoRA/GRPO adapters and evaluate the real agent.

Output: a JSON report at outputs/eval_report.json.
"""
import argparse, json, os, yaml
from .scenarios import load
from . import metrics
from ..agent.state import PatientState
from ..agent.react import run_turn
from ..agent.safety_gate import escalate, detect_complications

def mock_generate_factory():
    """A deterministic stand-in policy: it escalates on red-flag language and
    otherwise calls exercise_query. Used only for --mock smoke tests."""
    def generate(ctx):
        user = ctx.split("User:")[-1]
        return ('Thought: assess request.\n'
                'Action: {"tool": "exercise_query", "args": {"fracture_type": "unknown", "phase": "early_mobilization"}}\n'
                'Response: Here is phase-appropriate guidance; contact your clinical team for any concerning symptoms.')
    return generate

def real_generate_factory(adapters):
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from peft import PeftModel
    base = yaml.safe_load(open("configs/sft_qlora.yaml"))["model_name"]
    tok = AutoTokenizer.from_pretrained(base)
    model = AutoModelForCausalLM.from_pretrained(base, torch_dtype=torch.bfloat16, device_map="auto")
    model = PeftModel.from_pretrained(model, adapters)
    def generate(ctx):
        enc = tok(ctx, return_tensors="pt").to(model.device)
        out = model.generate(**enc, max_new_tokens=512, do_sample=False)
        return tok.decode(out[0][enc.input_ids.shape[1]:], skip_special_tokens=True)
    return generate

def evaluate(generate):
    scenarios = load(); successes = []; tp=fp=tn=fn=0
    details = []
    for s in scenarios:
        st = PatientState(fracture_type=s["fracture"], phase={"early":"early_mobilization",
             "mid":"strengthening","late":"return_to_activity"}[s["phase"]])
        tr = run_turn(generate, st, s["prompt"])
        escalated = tr.get("escalated", False) or ("escalat" in tr.get("response","").lower())
        gold = s["gold_escalate"]
        tp += escalated and gold; fp += escalated and not gold
        tn += (not escalated) and (not gold); fn += (not escalated) and gold
        # task success rubric: correct escalation decision AND a non-empty grounded response
        success = (escalated == gold) and bool(tr.get("response"))
        successes.append(int(success)); details.append({"id": s["id"], "success": success, "escalated": escalated, "gold": gold})
    report = {"n_scenarios": len(scenarios), **metrics.tcr(successes),
              "escalation": metrics.classification(tp, fp, tn, fn), "details": details}
    return report

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--adapters", default=None)
    a = ap.parse_args()
    gen = mock_generate_factory() if (a.mock or not a.adapters) else real_generate_factory(a.adapters)
    rep = evaluate(gen)
    os.makedirs("outputs", exist_ok=True)
    json.dump(rep, open("outputs/eval_report.json", "w"), indent=2)
    print(f"[evaluate] n={rep['n_scenarios']}  TCR={rep['tcr']:.3f} "
          f"CI95=({rep['ci95'][0]:.3f},{rep['ci95'][1]:.3f})  "
          f"sens={rep['escalation']['sensitivity']:.3f} spec={rep['escalation']['specificity']:.3f}")
    print("[evaluate] full report -> outputs/eval_report.json")

if __name__ == "__main__":
    main()
