"""
06_mcnemar_paired.py -- exact paired model comparison on the same 210 scenarios.
The 210 scenarios are shared across models, so TCR comparisons are PAIRED;
McNemar's test is the correct test (the unpaired z-test in script 01 is only a
conservative bound). INPUT: data_templates/per_scenario_success.csv with columns:
  scenario_id, <one 0/1 column per model> e.g. FractureAgent, GPT4o_5shot, ...
Run: python 06_mcnemar_paired.py
"""
import csv
from statsmodels.stats.contingency_tables import mcnemar
rows=list(csv.DictReader(open("data_templates/per_scenario_success.csv")))
models=[c for c in rows[0] if c!="scenario_id"]
ref="FractureAgent"
print(f"McNemar paired tests vs {ref}:")
for m in models:
    if m==ref: continue
    b=sum(int(r[ref])==1 and int(r[m])==0 for r in rows)  # ref win
    c=sum(int(r[ref])==0 and int(r[m])==1 for r in rows)  # other win
    res=mcnemar([[0,b],[c,0]], exact=(b+c<25))
    print(f"  vs {m:18s} discordant b={b} c={c}  stat={res.statistic:.2f}  p={res.pvalue:.2e}")
