#!/usr/bin/env bash
set -euo pipefail
# extract -> synthesize -> tool-traces -> quality filter -> SFT/GRPO builders -> split
python -m fractureagent.data.extract_chunk
python -m fractureagent.data.synthesize_dialogues "${SYNTH_FLAGS:---dry-run}"   # set SYNTH_FLAGS="" to use GPT-4o
python -m fractureagent.data.add_tool_traces
python -m fractureagent.data.quality_filter            # add --use-model to use DeBERTa
python -m fractureagent.data.build_sft
python -m fractureagent.data.build_grpo
python -m fractureagent.data.split
