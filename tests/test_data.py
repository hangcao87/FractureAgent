from pathlib import Path

from fractureagent.config import load_yaml
from fractureagent.data.build import build_dataset
from fractureagent.data.io import read_jsonl


def test_build_dataset_from_fixture(tmp_path: Path):
    config = load_yaml(Path("configs/data.yaml"))
    config["scenario_variants"] = 2
    manifest = build_dataset("data/examples/source_blocks.jsonl", tmp_path, config)
    assert manifest["chunks"] == 2
    assert manifest["examples"] > 0
    assert read_jsonl(tmp_path / "train.jsonl")
