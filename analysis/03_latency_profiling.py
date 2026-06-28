"""
03_latency_profiling.py -- per-query completion-time / latency profiling.
Reviewer 2.2: report wall-clock completion time per query to assess clinical
feasibility. INPUT: data_templates/latency_log.csv with columns:
  scenario_id, tool_used, n_react_steps, latency_seconds
Run: python 03_latency_profiling.py
"""
import csv, numpy as np
rows=list(csv.DictReader(open("data_templates/latency_log.csv")))
lat=np.array([float(r["latency_seconds"]) for r in rows])
print(f"Queries={len(lat)}")
print(f"Mean={lat.mean():.2f}s  Median={np.median(lat):.2f}s  "
      f"p90={np.percentile(lat,90):.2f}s  p95={np.percentile(lat,95):.2f}s  Max={lat.max():.2f}s")
# 95% CI of the mean via bootstrap
bs=[np.random.choice(lat,len(lat),replace=True).mean() for _ in range(10000)]
print(f"Mean 95% CI [{np.percentile(bs,2.5):.2f}, {np.percentile(bs,97.5):.2f}] s")
print("\nPer-tool median latency:")
from collections import defaultdict
d=defaultdict(list)
for r in rows: d[r["tool_used"]].append(float(r["latency_seconds"]))
for tool,v in sorted(d.items()): print(f"  {tool:18s} n={len(v):3d}  median={np.median(v):.2f}s")
