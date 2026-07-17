# Reproducibility workflow and release boundary

```text
Authorized source files
        |
        v
normalize -> chunk -> template/provider synthesis -> tool traces -> quality filter -> split
        |                                                               |
        +--> records/data_processing/run_manifest                         v
                                                       Swift `messages` JSONL export
                                                                      |
                                                                      v
                                                         ms-swift `swift sft`
                                                         QLoRA local adapter
                                                                      |
                                                                      v
                                         ReAct runtime + deterministic safety gate + evaluation
```

## Publicly released

- source ingestion and normalization logic;
- chunking, dialogue-template and tool-trace construction code;
- all training prompts and tool schemas;
- the ms-swift QLoRA configuration and Windows/Linux environment scripts;
- evaluation code, synthetic smoke-test fixtures and aggregate manuscript-reported results;
- run-record schemas for source provenance, training and evaluation.

## Not publicly released

- the curated training corpus and raw source downloads;
- patient-level or institution-specific records;
- trained model weights and LoRA adapters;
- API keys and private provider outputs.

The public repository is therefore a complete code-and-provenance recipe, not a distribution of restricted research materials. Requests concerning derived data can be sent to `hangcao87@163.com`; any response is subject to source licences, author approval and applicable institutional requirements.
