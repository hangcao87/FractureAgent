"""Evaluation metrics — formulas match Appendix A of the paper."""
from __future__ import annotations
import math
from statsmodels.stats.proportion import proportion_confint

def wilson_ci(k, n): return proportion_confint(k, n, 0.05, "wilson")
def clopper_pearson(k, n): return proportion_confint(k, n, 0.05, "beta")
def cohen_h(p1, p2): return 2*math.asin(math.sqrt(p1)) - 2*math.asin(math.sqrt(p2))
def cohen_d(m1, s1, n1, m2, s2, n2):
    sp = math.sqrt(((n1-1)*s1*s1 + (n2-1)*s2*s2) / (n1+n2-2))
    return (m1-m2)/sp if sp else float("nan")

def tcr(successes):
    k, n = sum(successes), len(successes)
    lo, hi = wilson_ci(k, n)
    return {"tcr": k/n, "k": k, "n": n, "ci95": (lo, hi)}

def classification(tp, fp, tn, fn):
    def safe(a, b): return a/b if b else float("nan")
    sens, spec = safe(tp, tp+fn), safe(tn, tn+fp)
    ppv, npv = safe(tp, tp+fp), safe(tn, tn+fn)
    f1 = safe(2*ppv*sens, (ppv+sens)) if not math.isnan(ppv*sens) else float("nan")
    out = {"sensitivity": sens, "specificity": spec, "ppv": ppv, "npv": npv,
           "fpr": safe(fp, fp+tn), "f1": f1, "tp": tp, "fp": fp, "tn": tn, "fn": fn}
    if tp+fn: out["sensitivity_ci95"] = clopper_pearson(tp, tp+fn)
    if tn+fp: out["specificity_ci95"] = clopper_pearson(tn, tn+fp)
    return out

def bleu4(hypotheses, references):
    """Corpus BLEU-4 via sacrebleu (references: list[list[str]])."""
    import sacrebleu
    return sacrebleu.corpus_bleu(hypotheses, references,
            smooth_method="exp", tokenize="13a").score / 100.0

def expected_calibration_error(confidences, correct, n_bins=10):
    ece, n = 0.0, len(confidences)
    for b in range(n_bins):
        lo, hi = b/n_bins, (b+1)/n_bins
        idx = [i for i,c in enumerate(confidences) if (c>lo and c<=hi)]
        if idx:
            acc = sum(correct[i] for i in idx)/len(idx)
            conf = sum(confidences[i] for i in idx)/len(idx)
            ece += len(idx)/n*abs(acc-conf)
    return ece

def brier(confidences, correct):
    return sum((c-o)**2 for c,o in zip(confidences, correct))/len(confidences)
