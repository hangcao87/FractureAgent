#!/usr/bin/env bash
set -euo pipefail
# Download open-access sources (rate-limited, robots-aware). Respect DATA_LICENSES.md.
python -m fractureagent.data.crawl_all
