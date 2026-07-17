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
        "Post-fracture rehabilitation requires individualized, phase-specific guidance as pain, function and exercise tolerance change over time, but "
        "many digital tools provide static information between clinic visits and do not integrate symptom assessment, evidence retrieval and safety "
        "escalation. To address this gap, we developed FractureAgent, a ReAct-style intelligent agent that combines a domain-adapted Qwen3.5-9B "
        "backbone with five typed tools for exercise retrieval, pain assessment, functional-progress tracking, literature retrieval and reminder planning. "
        "We adapted the model with QLoRA supervised instruction tuning on 18,742 synthetic rehabilitation dialogues and tool-use traces derived from "
        "open-access clinical and patient-education sources. Across automated functional metrics, expert clinical ratings and 210 simulated-patient "
        "scenarios spanning six fracture types and three rehabilitation phases, FractureAgent achieved a task completion rate of 91.4%, a mean "
        "clinical-appropriateness score of 4.21/5.00, pain-assessment concordance of 0.873, exercise-appropriateness of 0.896 and complication-detection "
        "sensitivity of 0.843, outperforming the evaluated baselines including the unfine-tuned Qwen3.5-9B backbone. These results indicate that "
        "tool-augmented language-model agents can provide context-responsive fracture-rehabilitation support in simulated settings, but they do not "
        "establish clinical effectiveness or readiness for deployment."
    )
    data_text = (
        "Availability of data and materials. The source materials were obtained from the open-access providers listed above and remain subject to their "
        "current terms of use. The curated training corpus is not included in the public repository because it is being retained for ongoing research, "
        "intellectual-property protection and grant-related work; no patient-level data are distributed. Reasonable requests concerning derived data "
        "may be directed to hangcao87@163.com, subject to source licences, author approval and any applicable institutional requirements."
    )
    code_text = (
        "Code availability. The public repository at https://github.com/hangcao87/FractureAgent contains the data-processing "
        "scripts, versioned training prompts, tool schemas and implementations, deterministic safety gate, ms-swift/Swift QLoRA configuration, training "
        "launchers, evaluation code and non-sensitive run-record templates. The trained FractureAgent weights, LoRA checkpoints, private credentials and "
        "curated training corpus are not publicly released at this stage. Users may reproduce the workflow with a legally obtained local base model and "
        "their own authorized data."
    )
    weight_text = (
        "Single-GPU training recipe (5): QLoRA fine-tuning that fits a 24 GB consumer GPU and runs in approximately 14 h on 2 x A100 GPUs. The code, "
        "prompt templates, ms-swift/Swift training configuration and evaluation scripts are available in the accompanying repository; trained model weights "
        "and the curated training corpus are not publicly released at this stage because they are being retained for ongoing research, intellectual-property "
        "protection and grant-related work."
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
