"""Unit tests for metrics (Appendix A). Run: pytest -q"""
from fractureagent.eval import metrics

def test_tcr_ci():
    r = metrics.tcr([1]*192 + [0]*18)   # 192/210 = 0.914
    assert abs(r["tcr"] - 0.914) < 1e-3
    assert 0.86 < r["ci95"][0] < 0.90 and 0.93 < r["ci95"][1] < 0.96

def test_classification():
    c = metrics.classification(tp=59, fp=6, tn=134, fn=11)
    assert abs(c["sensitivity"] - 0.843) < 0.01
    assert c["specificity"] > 0.9 and c["fpr"] < 0.06

def test_cohen_h():
    assert abs(metrics.cohen_h(0.914, 0.614) - 0.75) < 0.02
