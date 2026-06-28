"""
01_proportion_cis_and_tests.py
Reproduces CIs, significance tests, and effect sizes reported in the
FractureAgent manuscript (Tables 3-5; Statistical Analysis; Appendix S2).
Inputs are the aggregate point estimates + sample sizes already in the
manuscript (n=210). Deterministic; no private data needed.
Run:  python 01_proportion_cis_and_tests.py   Deps: numpy scipy statsmodels
"""
import numpy as np
from statsmodels.stats.proportion import proportion_confint, proportions_ztest

N = 210  # evaluation scenarios (shared across models -> paired design)
wilson = lambda k, n: proportion_confint(k, n, alpha=0.05, method="wilson")
cp     = lambda k, n: proportion_confint(k, n, alpha=0.05, method="beta")
cohen_h = lambda p1, p2: 2*np.arcsin(np.sqrt(p1)) - 2*np.arcsin(np.sqrt(p2))

TCR = {"Static rule-based":52.4,"GPT-4o (0-shot)":67.3,"GPT-4o (5-shot)":73.8,
       "LLaMA-3.1-8B-FT":79.5,"Qwen3.5-9B (base)":61.4,"FractureAgent":91.4}
K = {m: round(p/100*N) for m, p in TCR.items()}

print("TABLE 3 - TCR with Wilson 95% CI (n=210)")
for m, p in TCR.items():
    lo, hi = wilson(K[m], N)
    print(f"  {m:22s} {p:5.1f}%  ({K[m]:3d}/{N})  95% CI [{lo*100:4.1f}, {hi*100:4.1f}]")

print("\nFractureAgent vs baselines on TCR (unpaired z = conservative bound;")
print("  use McNemar in script 06 for the exact paired test)")
for m in TCR:
    if m == "FractureAgent": continue
    z, pval = proportions_ztest([K["FractureAgent"], K[m]], [N, N])
    h = cohen_h(K["FractureAgent"]/N, K[m]/N); d = (K["FractureAgent"]-K[m])/N*100
    print(f"  vs {m:22s} dTCR={d:5.1f}pp  z={z:5.2f}  p={pval:.2e}  h={h:.2f}")

print("\nFractureAgent per-dimension rate metrics, 95% CI")
for label, p, n in [("Pain-assessment concordance",0.873,210),
                    ("Exercise appropriateness",0.896,210)]:
    k = round(p*n); lo, hi = wilson(k, n)
    print(f"  {label:28s} {p:.3f}  95% CI [{lo:.3f}, {hi:.3f}]  (n={n})")
N_POS = 70   # <-- REPLACE with logged count of complication-positive scenarios
k = round(0.843*N_POS); lo, hi = cp(k, N_POS)
print(f"  {'Complication sensitivity':28s} {k/N_POS:.3f}  95% CI [{lo:.3f}, {hi:.3f}]"
      f"  (Clopper-Pearson, N_pos={N_POS}; CONFIRM)")

m_fa, sd_fa, n_lik, m_base = 4.21, 0.48, 60, 3.21
se = sd_fa/np.sqrt(n_lik)
print(f"\nClinical Likert: FractureAgent {m_fa} (SD {sd_fa}), "
      f"95% CI [{m_fa-1.96*se:.2f}, {m_fa+1.96*se:.2f}] (n=60)")
print(f"  Cohen's d vs Qwen base, pooled SD 0.50 = {(m_fa-m_base)/0.50:.2f} "
      f"(exact d needs baseline SDs; script 05)")

print("\nTABLE 4 - per-cell TCR Wilson 95% CI (n=12/cell): CIs are WIDE,")
print("  so per-cell values must NOT be read as a fine-grained ranking.")
cells = {"Distal radius":[93.2,91.7,94.1],"Proximal humerus":[89.4,91.2,93.5],
         "Hip fracture":[90.1,93.8,88.6],"Tibial plateau":[87.3,90.4,91.8],
         "Ankle fracture":[92.7,93.1,94.2],"Clavicle":[88.4,90.7,91.2]}
for fx, ps in cells.items():
    parts=[]
    for p in ps:
        k=round(p/100*12); lo,hi=wilson(k,12); parts.append(f"{p:4.1f}[{lo*100:.0f}-{hi*100:.0f}]")
    print(f"  {fx:18s} "+"  ".join(parts))
