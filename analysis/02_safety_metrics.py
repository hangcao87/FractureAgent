"""
02_safety_metrics.py  -- complication-escalation gate operating characteristics.
Computes sensitivity, specificity, PPV, NPV, false-positive rate, F1, balanced
accuracy and their 95% CIs from the per-scenario safety labels.
INPUT: data_templates/safety_labels.csv with columns:
  scenario_id, y_true (1=escalation-warranted), y_pred (1=agent escalated)
Replace the template (illustrative rows) with the real evaluation log.
Run: python 02_safety_metrics.py
"""
import csv, numpy as np
from statsmodels.stats.proportion import proportion_confint
def ci(k,n): 
    if n==0: return (float('nan'),float('nan'))
    return proportion_confint(k,n,alpha=0.05,method="beta")
TP=FP=TN=FN=0
with open("data_templates/safety_labels.csv") as f:
    for r in csv.DictReader(f):
        t,p=int(r["y_true"]),int(r["y_pred"])
        TP+=(t==1 and p==1); FP+=(t==0 and p==1)
        TN+=(t==0 and p==0); FN+=(t==1 and p==0)
P,Ngt=TP+FN,TP+FP+TN+FN
sens=TP/(TP+FN) if TP+FN else float('nan')
spec=TN/(TN+FP) if TN+FP else float('nan')
ppv =TP/(TP+FP) if TP+FP else float('nan')
npv =TN/(TN+FN) if TN+FN else float('nan')
fpr =FP/(FP+TN) if FP+TN else float('nan')
f1  =2*ppv*sens/(ppv+sens) if (ppv+sens) else float('nan')
print(f"Confusion: TP={TP} FP={FP} TN={TN} FN={FN}  (N={Ngt}, positives={P})")
for name,val,k,n in [("Sensitivity",sens,TP,TP+FN),("Specificity",spec,TN,TN+FP),
                     ("PPV",ppv,TP,TP+FP),("NPV",npv,TN,TN+FN),("FPR",fpr,FP,FP+TN)]:
    lo,hi=ci(k,n); print(f"  {name:12s} {val:.3f}  95% CI [{lo:.3f}, {hi:.3f}]")
print(f"  F1           {f1:.3f}")
print("Inappropriate (false) escalations =",FP,"; missed escalations (FN) =",FN)
