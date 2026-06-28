"""
04_calibration_hallucination.py -- factuality / calibration / hallucination.
Reviewer 3: report hallucination rate, factuality, calibration, uncertainty.
INPUT: data_templates/response_audit.csv with columns:
  scenario_id, confidence (0-1 self-reported or token-prob), correct (1/0),
  hallucinated (1 = contains an unsupported clinical claim, adjudicated)
Computes hallucination rate (+95% CI), Brier score, and Expected Calibration
Error (ECE, 10 bins). Run: python 04_calibration_hallucination.py
"""
import csv, numpy as np
from statsmodels.stats.proportion import proportion_confint
rows=list(csv.DictReader(open("data_templates/response_audit.csv")))
conf=np.array([float(r["confidence"]) for r in rows])
corr=np.array([int(r["correct"]) for r in rows])
hall=np.array([int(r["hallucinated"]) for r in rows])
k,n=hall.sum(),len(hall)
lo,hi=proportion_confint(k,n,alpha=0.05,method="wilson")
print(f"Hallucination rate = {k}/{n} = {k/n:.3f}  95% CI [{lo:.3f}, {hi:.3f}]")
print(f"Brier score = {np.mean((conf-corr)**2):.4f}")
bins=np.linspace(0,1,11); ece=0
for i in range(10):
    m=(conf>bins[i])&(conf<=bins[i+1])
    if m.sum(): ece+=m.sum()/n*abs(corr[m].mean()-conf[m].mean())
print(f"Expected Calibration Error (10-bin) = {ece:.4f}")
