"""
05_interrater_reliability.py -- expert-rating reliability + effect sizes.
Reviewer 1/4/5: ICC across 6 raters, per-dimension agreement, effect sizes.
INPUT: data_templates/expert_ratings_long.csv with columns:
  response_id, model, rater_id, dimension, score (1-5)
Computes ICC(2,k) overall, Cohen's d (FractureAgent vs each model) per
dimension with pooled SD. Run: python 05_interrater_reliability.py
"""
import csv, numpy as np
from collections import defaultdict
rows=list(csv.DictReader(open("data_templates/expert_ratings_long.csv")))
# ICC(2,k) two-way random, average measures, overall clinical score
by=defaultdict(dict)
for r in rows:
    if r["dimension"]=="clinical":
        by[r["response_id"]][r["rater_id"]]=float(r["score"])
M=np.array([[v[k] for k in sorted(v)] for v in by.values() if len(v)>1])
if len(M)>1:
    n,k=M.shape; gm=M.mean()
    MSR=k*((M.mean(1)-gm)**2).sum()/(n-1)
    MSC=n*((M.mean(0)-gm)**2).sum()/(k-1)
    MSE=(((M-M.mean(1,keepdims=True)-M.mean(0,keepdims=True)+gm)**2).sum())/((n-1)*(k-1))
    icc=(MSR-MSE)/(MSR+(MSC-MSE)/n)
    print(f"ICC(2,k) overall clinical score = {icc:.3f}  (n={n} responses, k={k} raters)")
# Cohen's d per dimension, FractureAgent vs others
def cohend(a,b):
    sp=np.sqrt(((len(a)-1)*a.var(ddof=1)+(len(b)-1)*b.var(ddof=1))/(len(a)+len(b)-2))
    return (a.mean()-b.mean())/sp if sp else float('nan')
sc=defaultdict(lambda: defaultdict(list))
for r in rows: sc[r["dimension"]][r["model"]].append(float(r["score"]))
print("\nCohen's d, FractureAgent vs baseline, per dimension:")
for dim,md in sc.items():
    if "FractureAgent" not in md: continue
    fa=np.array(md["FractureAgent"])
    for m,v in md.items():
        if m=="FractureAgent": continue
        print(f"  {dim:12s} vs {m:18s} d={cohend(fa,np.array(v)):.2f}")
