# Draft response to Reviewer 4

## Comment 1

**Reviewer comment:** The abstract should be converted to a single unstructured paragraph and shortened.

**Response:** We thank the reviewer for this helpful suggestion. We revised the abstract into a single unstructured paragraph and removed non-essential methodological detail while retaining the study objective, the ReAct multi-tool design, the evaluation setting, the principal performance results and the simulation-based limitation.

**Manuscript location:** Abstract, revised version.

## Comment 2

**Reviewer comment:** Please add a dedicated Code Availability statement and clarify whether source code, training scripts, tool implementations, prompts and model checkpoints are available.

**Response:** We agree that this clarification improves transparency and reproducibility. We added a dedicated Code Availability statement. The accompanying repository contains the data-processing pipeline, versioned prompts, tool schemas and implementations, deterministic safety-gate logic, ms-swift/Swift QLoRA configuration and launchers, evaluation code and synthetic fixtures. We do not release the curated training corpus, trained model weights or LoRA checkpoints at this stage because they are being retained for ongoing intellectual-property protection, follow-on validation and grant-related work. No patient-level data are distributed. The repository instead documents how users can supply a legally obtained local base model and reconstruct the data-processing and Swift training workflow. Derived-data requests may be directed to hangcao87@163.com, subject to source licences and author approval.

**Manuscript location:** Declarations, Code Availability.

## Risk check before submission

- Replace “revised version” with final page/line numbers after the journal-formatted manuscript is generated.
- Confirm that the public repository actually contains the listed files before submitting the response.
- If the journal requires a specific repository DOI or archived release, add it after the release is created.
- Keep the manuscript wording consistent: do not simultaneously claim that model weights “will be released openly” and that weights are withheld. The conclusion and any abstract sentence making that claim must be revised.
