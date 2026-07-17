"""Create the current-round tracked manuscript from the author's tracked DOCX.

The script preserves the source package and adds genuine Word revision markup
(w:del/w:ins) for the abstract, data availability, code availability, and the
weight-release sentence. It intentionally does not include training data or
model checkpoints.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import zipfile
from pathlib import Path

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML = "http://www.w3.org/XML/1998/namespace"
NS = {"w": W}


def qn(tag: str) -> str:
    return f"{{{W}}}{tag}"


def local_text(paragraph: etree._Element) -> str:
    return "".join((node.text or "") for node in paragraph.xpath(".//w:t|.//w:delText", namespaces=NS))


def next_change_id(root: etree._Element) -> int:
    values = []
    for node in root.xpath(".//*[@w:id]", namespaces=NS):
        try:
            values.append(int(node.get(qn("id"))))
        except (TypeError, ValueError):
            pass
    return max(values, default=0) + 1


def run_properties(paragraph: etree._Element) -> etree._Element | None:
    node = paragraph.find(".//w:r/w:rPr", namespaces=NS)
    return copy.deepcopy(node) if node is not None else None


def make_run(text: str, rpr: etree._Element | None, deleted: bool = False) -> etree._Element:
    run = etree.Element(qn("r"))
    if rpr is not None:
        run.append(copy.deepcopy(rpr))
    text_node = etree.SubElement(run, qn("delText" if deleted else "t"))
    if text[:1].isspace() or text[-1:].isspace():
        text_node.set(f"{{{XML}}}space", "preserve")
    text_node.text = text
    return run


def revision(tag: str, change_id: int, author: str) -> etree._Element:
    node = etree.Element(qn(tag))
    node.set(qn("id"), str(change_id))
    node.set(qn("author"), author)
    node.set(qn("date"), dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"))
    return node


def replace_paragraph(paragraph: etree._Element, new_text: str, change_id: int, author: str) -> int:
    old_text = local_text(paragraph)
    ppr = paragraph.find("w:pPr", namespaces=NS)
    rpr = run_properties(paragraph)
    for child in list(paragraph):
        if child is not ppr:
            paragraph.remove(child)
    if old_text:
        deletion = revision("del", change_id, author)
        deletion.append(make_run(old_text, rpr, deleted=True))
        paragraph.append(deletion)
        change_id += 1
    if new_text:
        insertion = revision("ins", change_id, author)
        insertion.append(make_run(new_text, rpr))
        paragraph.append(insertion)
        change_id += 1
    return change_id


def insert_paragraph_after(reference: etree._Element, text: str, change_id: int, author: str) -> int:
    paragraph = etree.Element(qn("p"))
    ppr = reference.find("w:pPr", namespaces=NS)
    if ppr is not None:
        paragraph.append(copy.deepcopy(ppr))
    insertion = revision("ins", change_id, author)
    insertion.append(make_run(text, run_properties(reference)))
    paragraph.append(insertion)
    reference.addnext(paragraph)
    return change_id + 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_docx")
    parser.add_argument("--out", required=True)
    parser.add_argument("--author", default="Authors")
    args = parser.parse_args()

    abstract = (
        "Fracture rehabilitation must adapt as pain, function and warning signs change across healing phases, but many digital tools provide static "
        "information and cannot coordinate exercise selection, symptom assessment, progress monitoring and safety escalation. To address this gap, we "
        "developed FractureAgent, a reasoning-and-action (ReAct)-style system that couples a domain-adapted Qwen3.5-9B backbone with five typed "
        "rehabilitation tools and a deterministic safety gate to provide phase-aware support. The model was adapted using quantized low-rank adaptation "
        "(QLoRA) supervised instruction tuning on 18,742 synthetic rehabilitation dialogues and tool-use traces derived from open-access clinical and "
        "patient-education sources. We evaluated FractureAgent using automated functional metrics, expert clinical ratings and 210 simulated-patient "
        "scenarios spanning six fracture types and three rehabilitation phases. It achieved a task completion rate of 91.4%, a mean clinical-appropriateness "
        "score of 4.21/5.00, pain-assessment concordance of 0.873, exercise-appropriateness of 0.896 and complication-detection sensitivity of 0.843, "
        "outperforming the evaluated baselines, including the unfine-tuned Qwen3.5-9B backbone. These findings indicate that FractureAgent can coordinate "
        "multiple rehabilitation tasks and provide adaptive support in simulated settings, addressing the technical limitations of static digital guidance; "
        "however, they do not establish clinical effectiveness or readiness for deployment."
    )
    data_text = (
        "Availability of data and materials. The source materials were obtained from the open-access providers listed above and remain subject to their "
        "current terms of use. The curated training corpus is not included in the public repository because the assembled corpus is being retained for "
        "ongoing research, intellectual-property protection and planned grant-supported work; no patient-level data are distributed. Reasonable requests "
        "concerning derived data may be directed to hangcao87@163.com, subject to source licences, author approval and any applicable institutional "
        "requirements."
    )
    code_text = (
        "Code availability. The public repository at https://github.com/hangcao87/FractureAgent contains the data-processing scripts, versioned training "
        "prompts, tool schemas and implementations, deterministic safety gate, ms-swift/Swift QLoRA configuration and launchers, evaluation code, synthetic "
        "fixtures and non-sensitive run-record templates. The curated training corpus is not publicly distributed because the source materials remain "
        "subject to their original providers' terms and the assembled corpus is being retained for ongoing research, intellectual-property protection and "
        "planned grant-supported work. The trained FractureAgent weights and LoRA checkpoints are not publicly released because follow-on validation and "
        "intellectual-property assessment are ongoing and the resulting model forms part of the same planned research programme. No patient-level data or "
        "private credentials are included. Users may reproduce the disclosed workflow with a legally obtained local base model and their own authorized "
        "data; reasonable requests concerning derived data may be directed to hangcao87@163.com, subject to source licences, author approval and applicable "
        "institutional requirements."
    )
    weight_text = (
        "Single-GPU training recipe (5): QLoRA fine-tuning that fits a 24 GB consumer GPU and runs in approximately 14 h on 2 x A100 GPUs. The code, "
        "prompt templates, ms-swift/Swift training configuration and evaluation scripts are available in the accompanying repository; trained model weights "
        "and the curated training corpus are not publicly released because source-use terms, follow-on validation, intellectual-property assessment and "
        "planned grant-supported work remain ongoing."
    )
    intro_corpus_text = (
        "Source-derived training corpus (§4). We assemble an 18,742-example fine-tuning corpus from open-access clinical sources (AAOS CPGs, AO Surgery "
        "Reference, PubMed OA, PhysioNet, WikiDoc / MedlinePlus). Of these examples, 12,891 carry explicit Thought–Act–Obs–Resp tool traces (Eq. 1). A "
        "stratified expert audit (3 surgeons + 3 PTs) confirms clinical plausibility (ICC = 0.83). The curated corpus is not publicly distributed because "
        "the source materials remain subject to their original providers' terms and the assembled corpus is retained for ongoing research, "
        "intellectual-property protection and planned grant-supported work."
    )
    intro_training_text = (
        "Public training recipe (§5). We adapt the Qwen3.5-9B backbone with QLoRA (rank r = 16, scaling α = 32, NF4 quantization) on a 70:30 mixture of "
        "agent-format and standard dialogue data, fitting on a 24 GB consumer GPU. The public repository provides the data-processing code, prompts and "
        "ms-swift/Swift configuration needed to reconstruct the pipeline with a legally obtained local base model and authorized source materials; the "
        "curated corpus and trained checkpoints are not included."
    )
    discussion_heading_text = "7.2 What the source-derived corpus contributes (Contribution 2)"
    finding_text = (
        "Finding. Fine-tuning, not the backbone choice, is what closes the gap with proprietary models. The same Qwen3.5-9B that scores 61.4% TCR with "
        "the bare base model rises to 91.4% TCR after the FractureAgent recipe (+30.0 pp) — a margin substantially larger than any of the cross-architecture "
        "comparisons (e.g. LLaMA-3.1-8B-FT 79.5 → FractureAgent 91.4 = 11.9 pp). This is the central empirical claim of the paper: an open backbone of "
        "moderate size, fine-tuned on a curated source-derived corpus, becomes competitive with — and on these clinical metrics, surpasses — a much larger "
        "closed model with 5-shot prompting."
    )
    safety_finding_text = (
        "Finding. The per-dimension breakdown localizes the source of the overall lead of FractureAgent. The wins concentrate where domain knowledge and "
        "explicit safety reasoning matter most (clinical accuracy, safety, completeness) and shrink on dimensions that reward generic conversational "
        "fluency (readability, empathy). The safety advantage in particular is driven by the deterministic Eq. 5 gate rather than by raw LLM judgement — "
        "a design choice whose rule predicates and implementation are available in the public code for independent reconstruction."
    )
    ablation_text = (
        "The ablation in §6.6 (Table 5, Figure 8) shows that the five tools cover orthogonal capabilities rather than acting as interchangeable wrappers "
        "around the LLM: removing exercise query collapses TCR and exercise-appropriateness but barely moves complication sensitivity, whereas removing "
        "pain assess does the inverse (complication sensitivity drops from 0.843 to 0.601 whereas exercise-appropriateness stays at 0.887). The deterministic "
        "escalation gate (Eq. 5) is the design choice that produces the per-dimension safety margin visible in Figure 7 (+0.62 Likert vs LLaMA-FT, +0.92 vs "
        "GPT-4o 0-shot). Architecturally, this isolates safety behaviours from LLM discretion; the public rule predicates and implementation allow this "
        "component to be reconstructed independently of the authors' non-public trained checkpoint."
    )
    discussion_corpus_text = (
        "The 18,742-example source-derived corpus, including 12,891 explicit Thought–Act–Obs–Resp tool traces, supplies the domain-specific supervision "
        "used to adapt FractureAgent. The error analysis in §6.7 (Figure 9) identifies tool-orchestration mistakes as the dominant residual failure mode "
        "(9 of 18 failures); these are precisely the failures most likely to be addressed by additional tool-trace examples, suggesting that the current "
        "corpus is sufficient to demonstrate the recipe but would benefit from continued growth in v2."
    )
    conclusion_corpus_text = (
        "Source-derived corpus (§4, Figure 5) — 18,742 examples (12,891 with explicit tool traces) constructed from open-access clinical sources. Expert "
        "audit of the corpus reaches ICC = 0.83. The curated corpus itself is not publicly distributed for the reasons stated in the Data and Code "
        "Availability declarations."
    )
    conclusion_summary_text = (
        "Trained exclusively on material derived from open-access sources and fine-tunable with consumer-grade GPU hardware, FractureAgent provides a "
        "documented foundation for AI-augmented rehabilitation research. The public code enables reconstruction of the processing and training workflow "
        "with a legally obtained local base model and authorized data, while the authors' curated corpus and trained checkpoints remain non-public for the "
        "reasons stated above. Prospective clinical validation in orthopaedic outpatient settings, expansion to paediatric and post-surgical populations, "
        "and integration with objective sensor-based functional assessment are necessary before any deployment-ready claim can be made. As a "
        "proof-of-concept, this work indicates that a moderately sized open-weight LLM, when paired with structured tool use and domain-specific instruction "
        "tuning, can generate clinically plausible guidance in simulated fracture-rehabilitation scenarios."
    )

    with zipfile.ZipFile(args.input_docx, "r") as source:
        document = etree.fromstring(source.read("word/document.xml"))
        settings = etree.fromstring(source.read("word/settings.xml"))
        paragraphs = document.xpath(".//w:body/w:p", namespaces=NS)
        change_id = next_change_id(document)

        def find(prefix: str, last: bool = False):
            matches = [p for p in paragraphs if local_text(p).startswith(prefix)]
            return (matches[-1] if last else (matches[0] if matches else None))

        for prefix, text in [("Background.", abstract), ("Methods.", ""), ("Results.", ""), ("Conclusions.", "")]:
            paragraph = find(prefix)
            if paragraph is None:
                raise RuntimeError(f"Cannot find abstract paragraph: {prefix}")
            change_id = replace_paragraph(paragraph, text, change_id, args.author)

        for prefix, text, last in [
            ("Open-data corpus (§4).", intro_corpus_text, False),
            ("Single-GPU training recipe (§5).", intro_training_text, False),
            ("Finding. Fine-tuning, not the backbone choice", finding_text, False),
            ("Finding. The per-dimension breakdown", safety_finding_text, False),
            ("The ablation in §6.6", ablation_text, False),
            ("7.2 What the open-data corpus buys", discussion_heading_text, False),
            ("The 18,742-example corpus is the largest", discussion_corpus_text, False),
            ("Open-data corpus (§4, Figure 5)", conclusion_corpus_text, True),
            ("Trained exclusively on freely available open-access data", conclusion_summary_text, False),
        ]:
            paragraph = find(prefix, last=last)
            if paragraph is None:
                raise RuntimeError(f"Cannot find consistency paragraph: {prefix}")
            change_id = replace_paragraph(paragraph, text, change_id, args.author)

        paragraph = find("Single-GPU training recipe", last=True)
        if paragraph is None:
            raise RuntimeError("Cannot find the conclusion training-recipe paragraph")
        change_id = replace_paragraph(paragraph, weight_text, change_id, args.author)

        paragraph = find("Availability of data and materials.")
        if paragraph is None:
            raise RuntimeError("Cannot find the data availability paragraph")
        change_id = replace_paragraph(paragraph, data_text, change_id, args.author)
        change_id = insert_paragraph_after(paragraph, code_text, change_id, args.author)

        if settings.find("w:trackRevisions", namespaces=NS) is None:
            settings.insert(0, etree.Element(qn("trackRevisions")))

        overrides = {
            "word/document.xml": etree.tostring(document, xml_declaration=True, encoding="UTF-8", standalone="yes"),
            "word/settings.xml": etree.tostring(settings, xml_declaration=True, encoding="UTF-8", standalone="yes"),
        }
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED) as target:
            for item in source.infolist():
                target.writestr(item, overrides.get(item.filename, source.read(item.filename)))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
