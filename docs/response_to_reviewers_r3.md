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

We sincerely thank the Reviewer for the positive assessment and for recognizing the revisions made in the previous round. We have continued to improve the accompanying repository. The public `main` branch contains the complete data-processing code, versioned prompts, tool schemas and implementations, deterministic safety gate, ms-swift/Swift QLoRA training configuration and launchers, evaluation code, synthetic fixtures and non-sensitive reproducibility-record templates. The curated training corpus and trained model weights are not included for the source-licence, ongoing-validation and intellectual-property reasons detailed in our response to Comment 4.2. The repository is available at https://github.com/hangcao87/FractureAgent.

## Response to Reviewer 4

### Comment 4.1

**Reviewer comment**

The abstract would benefit from revision to better align with the journal’s format and improve readability. The current abstract is structured using subheadings (Background, Methods, Results, Conclusions) and is relatively lengthy. Consider converting it into a single unstructured paragraph and reducing its length by focusing on the most essential methodological details and key findings.

**Response**

We agree with the Reviewer. The original abstract did not state the clinical-support gap and the design rationale sufficiently clearly. We replaced the four-part structured abstract with a single unstructured paragraph and reduced it from 461 to 195 words, within the journal's 200-word limit. The revision now follows a problem-gap-method-evidence-boundary sequence: it first explains why static digital guidance cannot coordinate changing rehabilitation needs, then shows how the five-tool ReAct architecture and deterministic safety gate address that gap, reports the principal quantitative findings and limits the conclusion to simulated technical feasibility. The complete revised abstract is reproduced below.

**Revised abstract (complete text):**

> Fracture rehabilitation must adapt as pain, function and warning signs change across healing phases, but many digital tools provide static information and cannot coordinate exercise selection, symptom assessment, progress monitoring and safety escalation. To address this gap, we developed FractureAgent, a reasoning-and-action (ReAct)-style system that couples a domain-adapted Qwen3.5-9B backbone with five typed rehabilitation tools and a deterministic safety gate to provide phase-aware support. The model was adapted using quantized low-rank adaptation (QLoRA) supervised instruction tuning on 18,742 synthetic rehabilitation dialogues and tool-use traces derived from open-access clinical and patient-education sources. We evaluated FractureAgent using automated functional metrics, expert clinical ratings and 210 simulated-patient scenarios spanning six fracture types and three rehabilitation phases. It achieved a task completion rate of 91.4%, a mean clinical-appropriateness score of 4.21/5.00, pain-assessment concordance of 0.873, exercise-appropriateness of 0.896 and complication-detection sensitivity of 0.843, outperforming the evaluated baselines, including the unfine-tuned Qwen3.5-9B backbone. These findings indicate that FractureAgent can coordinate multiple rehabilitation tasks and provide adaptive support in simulated settings, addressing the technical limitations of static digital guidance; however, they do not establish clinical effectiveness or readiness for deployment.

**Manuscript location:** Abstract.

### Comment 4.2

**Reviewer comment**

To enhance transparency and reproducibility, please consider adding a dedicated “Code Availability” statement. The manuscript provides substantial methodological detail; however, it is currently unclear whether the source code, training scripts, tool implementations, prompts, or model checkpoints are publicly available. If these resources cannot be shared, the authors should explicitly state this and provide the reason.

**Response**

We agree that the original manuscript did not make the release boundary sufficiently clear. We added a dedicated Code Availability paragraph under Declarations and revised related statements in the Introduction, Discussion and Conclusion for consistency. The public repository contains the data-processing code, versioned prompts, tool schemas and implementations, deterministic safety gate, ms-swift/Swift QLoRA configuration and launchers, evaluation code, synthetic fixtures and non-sensitive run-record templates. The curated training corpus is not redistributed because its source materials remain subject to the original providers' terms and the assembled corpus is being retained for ongoing research, intellectual-property protection and planned grant-supported work. The trained model weights and LoRA checkpoints are not released because follow-on validation and intellectual-property assessment remain ongoing and the resulting model is part of the same planned research programme. No patient-level data or private credentials are distributed. The complete statement added to the manuscript is reproduced below.

**Revised Code Availability statement (complete text):**

> Code availability. The public repository at https://github.com/hangcao87/FractureAgent contains the data-processing scripts, versioned training prompts, tool schemas and implementations, deterministic safety gate, ms-swift/Swift QLoRA configuration and launchers, evaluation code, synthetic fixtures and non-sensitive run-record templates. The curated training corpus is not publicly distributed because the source materials remain subject to their original providers' terms and the assembled corpus is being retained for ongoing research, intellectual-property protection and planned grant-supported work. The trained FractureAgent weights and LoRA checkpoints are not publicly released because follow-on validation and intellectual-property assessment are ongoing and the resulting model forms part of the same planned research programme. No patient-level data or private credentials are included. Users may reproduce the disclosed workflow with a legally obtained local base model and their own authorized data; reasonable requests concerning derived data may be directed to hangcao87@163.com, subject to source licences, author approval and applicable institutional requirements.

**Manuscript location:** Introduction, contribution summary; Discussion, Section 7.2; Conclusion, Section 8; Declarations, Availability of data and materials and Code availability.

## Manuscript change checklist

- Abstract: converted Background/Methods/Results/Conclusions into a 195-word unstructured paragraph and reproduced the complete revision above.
- Declarations: stated separately why the curated training corpus and trained weights/checkpoints are not publicly distributed and added the contact route for derived-data requests.
- Declarations: added a dedicated Code Availability statement covering data processing, prompts, tool implementations, Swift training configuration, evaluation code and run records.
- Introduction and Discussion: removed ambiguous claims that the curated corpus was an open release or that the full model was reproducible from publicly released project weights and data.
- Conclusion: removed the inconsistent statement that model weights would be released openly and replaced it with the actual release boundary.
- Repository: added Swift-only installation, data export, QLoRA SFT, inference, evaluation and run-record workflows; no training data or checkpoints were added.

## Missing information / risk flags

- Author confirmation before submission: all co-authors should approve the stated non-public release boundary and be prepared to respond to reasonable derived-data requests.
- Journal-policy risk: Scientific Reports may request data necessary to evaluate the manuscript's claims; the access-request wording should therefore be checked during submission.

Sincerely,
Dr Xiao Ouyang and Dr Weijuan Gong
Corresponding authors, on behalf of all authors
