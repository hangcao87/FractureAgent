"""Polite HTTP helpers: robots.txt enforcement, descriptive UA, rate limiting,
on-disk caching, and a checksum manifest so downloads are reproducible.

These safeguards are intentional. Do not bypass robots or remove the delay —
respect each source's Terms of Service (see DATA_LICENSES.md)."""
from __future__ import annotations
import hashlib, json, os, time, urllib.robotparser as rp
from urllib.parse import urlparse
import requests

UA = ("FractureAgent-research-crawler/1.0 "
      "(+https://github.com/ORG/FractureAgent; contact: you@example.org)")
_LAST: dict[str, float] = {}
_ROBOTS: dict[str, rp.RobotFileParser] = {}

def _robots(url: str) -> rp.RobotFileParser:
    host = urlparse(url).scheme + "://" + urlparse(url).netloc
    if host not in _ROBOTS:
        r = rp.RobotFileParser(); r.set_url(host + "/robots.txt")
        try: r.read()
        except Exception: pass
        _ROBOTS[host] = r
    return _ROBOTS[host]

def allowed(url: str) -> bool:
    try: return _robots(url).can_fetch(UA, url)
    except Exception: return True

def _throttle(url: str, delay: float):
    host = urlparse(url).netloc
    dt = time.time() - _LAST.get(host, 0.0)
    if dt < delay: time.sleep(delay - dt)
    _LAST[host] = time.time()

def get(url: str, cache_dir: str, delay: float = 2.0, params=None,
        headers=None, manifest: str | None = None) -> str | None:
    """GET with robots check, rate limit and disk cache. Returns text or None."""
    os.makedirs(cache_dir, exist_ok=True)
    key = hashlib.sha1((url + json.dumps(params or {}, sort_keys=True)).encode()).hexdigest()
    path = os.path.join(cache_dir, key + ".html")
    if os.path.exists(path):
        return open(path, encoding="utf-8", errors="ignore").read()
    if not allowed(url):
        print(f"[robots] disallowed, skipping: {url}"); return None
    _throttle(url, delay)
    h = {"User-Agent": UA}; h.update(headers or {})
    try:
        resp = requests.get(url, params=params, headers=h, timeout=30)
    except Exception as e:
        print(f"[http] error {url}: {e}"); return None
    if resp.status_code != 200:
        print(f"[http] {resp.status_code} {url}"); return None
    open(path, "w", encoding="utf-8").write(resp.text)
    if manifest:
        with open(manifest, "a") as m:
            m.write(json.dumps({"url": resp.url, "sha256":
                     hashlib.sha256(resp.content).hexdigest(),
                     "bytes": len(resp.content), "ts": time.time()}) + "\n")
    return resp.text
