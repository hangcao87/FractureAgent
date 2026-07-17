# Point-by-Point Response to Reviewers

**FractureAgent: A Multi-Tool LLM-Based Intelligent Agent for Personalized Fracture Rehabilitation Management**
**Journal:** Scientific Reports
**Decision:** Minor Revision
**Manuscript ID:** 0d10e894-9f9f-41a6-9d8e-f7f456b33960

Dear Editor and Reviewers,

We sincerely thank the Editor and the Reviewers for their careful assessment and constructive suggestions. We have revised the manuscript and the accompanying research repository to improve abstract readability, code transparency and reproducibility. The revised manuscript is supplied as a tracked-change file. Our point-by-point responses are provided below.

## Response to Reviewer 1

**Reviewer comment**

Thank you.

**Response**

We thank the Reviewer for the positive assessment. We have nevertheless made the cross-cutting transparency revision requested in this round, including the unstructured abstract and the dedicated Code Availability statement.

## Response to Reviewer 2

**Reviewer comment**

The authors have matched all the previously highlighted points. Hence, it is now worthy of publication and I hope it will reach the widest audience possible. https://github.com/hangcao87/FractureAgent

**Response**

We sincerely thank the Reviewer for the positive assessment and for recognizing the revisions made in the previous round. We have continued to improve the accompanying repository. The public `main` branch contains the complete data-processing code, versioned prompts, tool schemas and implementations, deterministic safety gate, ms-swift/Swift QLoRA training configuration and launchers, evaluation code, and non-sensitive reproducibility-record templates. The training data and trained model weights are not included. The repository is available at https://github.com/hangcao87/FractureAgent.

## Response to Reviewer 4

### Comment 4.1

**Reviewer comment**

The abstract would benefit from revision to better align with the journal’s format and improve readability. The current abstract is structured using subheadings (Background, Methods, Results, Conclusions) and is relatively lengthy. Consider converting it into a single unstructured paragraph and reducing its length by focusing on the most essential methodological details and key findings.

**Response**

We agree with the Reviewer. We replaced the structured abstract with a single unstructured paragraph and shortened it while clarifying the argument flow: the clinical-support gap is stated first, followed by the proposed tool-augmented method, the essential training and evaluation design, the principal quantitative findings and the simulation-based limitation.

**Manuscript location:** Abstract.

### Comment 4.2

**Reviewer comment**

To enhance transparency and reproducibility, please consider adding a dedicated “Code Availability” statement. The manuscript provides substantial methodological detail; however, it is currently unclear whether the source code, training scripts, tool implementations, prompts, or model checkpoints are publicly available. If these resources cannot be shared, the authors should explicitly state this and provide the reason.

**Response**

We agree that a dedicated statement is needed. We added a separate Code Availability paragraph under Declarations. The public repository contains the data-processing scripts, versioned training prompts, tool schemas and implementations, the deterministic safety gate, the ms-swift/Swift QLoRA configuration and launchers, evaluation code and non-sensitive run-record templates. The trained model weights, LoRA checkpoints, private credentials and the curated training corpus are not publicly released at this stage because they are being retained for ongoing research, intellectual-property protection and grant-related work. No patient-level data are distributed. Reasonable requests concerning derived data may be directed to hangcao87@163.com, subject to source licences, author approval and applicable institutional requirements.

**Manuscript location:** Declarations, Code availability; Availability of data and materials; Section 8, Conclusion.

## Manuscript change checklist

- Abstract: converted Background/Methods/Results/Conclusions into one unstructured paragraph and shortened the content.
- Declarations: revised data-availability wording to state that the curated training corpus is not publicly distributed and added the contact route for derived-data requests.
- Declarations: added a dedicated Code Availability statement covering data processing, prompts, tool implementations, Swift training configuration, evaluation code and run records.
- Conclusion: removed the inconsistent statement that model weights would be released openly and replaced it with the actual release boundary.
- Repository: added Swift-only installation, data export, QLoRA SFT, inference, evaluation and run-record workflows; no training data or checkpoints were added.

## Missing information / risk flags

None for the supplied comments. Before submission, confirm that the journal permits the stated access-request route and that the public branch contains the files listed above.

Sincerely,
Dr Xiao Ouyang and Dr Weijuan Gong
Corresponding authors, on behalf of all authors
