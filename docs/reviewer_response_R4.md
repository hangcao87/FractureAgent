# Draft response to Reviewer 4

## Comment 1

**Reviewer comment:** The abstract would benefit from revision to better align with the journal's format and improve readability. The current abstract is structured using subheadings (Background, Methods, Results, Conclusions) and is relatively lengthy. Consider converting it into a single unstructured paragraph and reducing its length by focusing on the most essential methodological details and key findings.

**Response:** We agree with the Reviewer. The original abstract did not state the clinical-support gap and the design rationale sufficiently clearly. We replaced the four-part structured abstract with a single unstructured paragraph and reduced it from 461 to 195 words, within the journal's 200-word limit. The revision now follows a problem-gap-method-evidence-boundary sequence and limits the conclusion to simulated technical feasibility.

**Revised abstract (complete text):**

> Fracture rehabilitation must adapt as pain, function and warning signs change across healing phases, but many digital tools provide static information and cannot coordinate exercise selection, symptom assessment, progress monitoring and safety escalation. To address this gap, we developed FractureAgent, a reasoning-and-action (ReAct)-style system that couples a domain-adapted Qwen3.5-9B backbone with five typed rehabilitation tools and a deterministic safety gate to provide phase-aware support. The model was adapted using quantized low-rank adaptation (QLoRA) supervised instruction tuning on 18,742 synthetic rehabilitation dialogues and tool-use traces derived from open-access clinical and patient-education sources. We evaluated FractureAgent using automated functional metrics, expert clinical ratings and 210 simulated-patient scenarios spanning six fracture types and three rehabilitation phases. It achieved a task completion rate of 91.4%, a mean clinical-appropriateness score of 4.21/5.00, pain-assessment concordance of 0.873, exercise-appropriateness of 0.896 and complication-detection sensitivity of 0.843, outperforming the evaluated baselines, including the unfine-tuned Qwen3.5-9B backbone. These findings indicate that FractureAgent can coordinate multiple rehabilitation tasks and provide adaptive support in simulated settings, addressing the technical limitations of static digital guidance; however, they do not establish clinical effectiveness or readiness for deployment.

**Manuscript location:** Abstract.

## Comment 2

**Reviewer comment:** To enhance transparency and reproducibility, please consider adding a dedicated Code Availability statement. The manuscript provides substantial methodological detail; however, it is currently unclear whether the source code, training scripts, tool implementations, prompts, or model checkpoints are publicly available. If these resources cannot be shared, the authors should explicitly state this and provide the reason.

**Response:** We agree that this clarification improves transparency and reproducibility. We added a dedicated Code Availability statement. The accompanying repository contains the data-processing pipeline, versioned prompts, tool schemas and implementations, deterministic safety-gate logic, ms-swift/Swift QLoRA configuration and launchers, evaluation code, synthetic fixtures and non-sensitive run-record templates. The curated training corpus is not publicly distributed because its source materials remain subject to their original providers' terms and the assembled corpus is being retained for ongoing research, intellectual-property protection and planned grant-supported work. The trained model weights and LoRA checkpoints are not released because follow-on validation and intellectual-property assessment remain ongoing and the resulting model is part of the same planned research programme. No patient-level data or private credentials are distributed. The repository documents how users can supply a legally obtained local base model and authorized data to reconstruct the disclosed processing and Swift training workflow. Derived-data requests may be directed to hangcao87@163.com, subject to source licences and author approval.

**Manuscript location:** Introduction, contribution summary; Discussion, Section 7.2; Conclusion, Section 8; Declarations, Availability of data and materials and Code availability.

## Risk check before submission

- Confirm that all co-authors approve the stated non-public release boundary.
- Confirm that the public repository contains every listed public file.
- If the journal requires a repository DOI or archived release, add it after creating the release.
- Do not describe the curated corpus or trained weights as an open release elsewhere in the manuscript.
