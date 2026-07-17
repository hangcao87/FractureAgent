"""Create the current-round tracked manuscript from a clean prior-round DOCX.

Only the changes requested in the present review round are marked: the third
affiliation correction, the unstructured abstract, a dedicated Code
Availability statement, and the directly contradictory weight-release sentence.
The input must contain no pre-existing tracked revisions.
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


def local_text(node: etree._Element) -> str:
    return "".join((part.text or "") for part in node.xpath(".//w:t|.//w:delText", namespaces=NS))


def next_change_id(root: etree._Element) -> int:
    values = []
    for node in root.xpath(".//*[@w:id]", namespaces=NS):
        try:
            values.append(int(node.get(qn("id"))))
        except (TypeError, ValueError):
            pass
    return max(values, default=0) + 1


def run_properties(node: etree._Element) -> etree._Element | None:
    rpr = node.find(".//w:r/w:rPr", namespaces=NS)
    return copy.deepcopy(rpr) if rpr is not None else None


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


def append_revision(paragraph: etree._Element, tag: str, text: str, rpr: etree._Element | None,
                    change_id: int, author: str) -> int:
    wrapper = revision(tag, change_id, author)
    wrapper.append(make_run(text, rpr, deleted=(tag == "del")))
    paragraph.append(wrapper)
    return change_id + 1


def replace_paragraph(paragraph: etree._Element, new_text: str, change_id: int, author: str) -> int:
    old_text = local_text(paragraph)
    ppr = paragraph.find("w:pPr", namespaces=NS)
    rpr = run_properties(paragraph)
    for child in list(paragraph):
        if child is not ppr:
            paragraph.remove(child)
    if old_text:
        change_id = append_revision(paragraph, "del", old_text, rpr, change_id, author)
    if new_text:
        change_id = append_revision(paragraph, "ins", new_text, rpr, change_id, author)
    return change_id


def replace_after_first_run(paragraph: etree._Element, new_text: str, change_id: int, author: str) -> int:
    """Preserve the superscript affiliation marker and replace the affiliation text."""
    runs = paragraph.findall("w:r", namespaces=NS)
    if len(runs) < 2:
        raise RuntimeError("Affiliation paragraph does not have the expected marker and text runs")
    marker = runs[0]
    children = list(paragraph)
    marker_index = children.index(marker)
    replaced = children[marker_index + 1:]
    old_text = "".join(local_text(child) for child in replaced)
    rpr = run_properties(runs[1])
    for child in replaced:
        paragraph.remove(child)
    change_id = append_revision(paragraph, "del", old_text, rpr, change_id, author)
    return append_revision(paragraph, "ins", new_text, rpr, change_id, author)


def replace_substring(paragraph: etree._Element, old: str, new: str, change_id: int, author: str) -> int:
    """Track only a target sentence while leaving the rest of the paragraph unchanged."""
    full_text = local_text(paragraph)
    if old not in full_text:
        raise RuntimeError(f"Cannot find target sentence: {old}")
    before, after = full_text.split(old, 1)
    ppr = paragraph.find("w:pPr", namespaces=NS)
    rpr = run_properties(paragraph)
    for child in list(paragraph):
        if child is not ppr:
            paragraph.remove(child)
    if before:
        paragraph.append(make_run(before, rpr))
    change_id = append_revision(paragraph, "del", old, rpr, change_id, author)
    change_id = append_revision(paragraph, "ins", new, rpr, change_id, author)
    if after:
        paragraph.append(make_run(after, rpr))
    return change_id


def insert_paragraph_after(reference: etree._Element, text: str, change_id: int, author: str) -> int:
    paragraph = etree.Element(qn("p"))
    ppr = reference.find("w:pPr", namespaces=NS)
    if ppr is not None:
        paragraph.append(copy.deepcopy(ppr))
    change_id = append_revision(paragraph, "ins", text, run_properties(reference), change_id, author)
    reference.addnext(paragraph)
    return change_id


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
    affiliation = " Department of Surgery, Xuzhou New Healthy Geriatric Hospital, Xuzhou 221007, Jiangsu Province, China"
    code_text = (
        "Code availability. The public repository at https://github.com/hangcao87/FractureAgent contains the data-processing scripts, versioned training "
        "prompts, tool schemas and implementations, deterministic safety gate, ms-swift QLoRA configuration and launchers, evaluation code, synthetic "
        "fixtures and non-sensitive run-record templates. The curated training corpus is not publicly distributed because the source materials remain "
        "subject to their original providers' terms and the assembled corpus is being retained for ongoing research, intellectual-property protection and "
        "planned grant-supported work. The trained FractureAgent weights and LoRA checkpoints are not publicly released because follow-on validation and "
        "intellectual-property assessment are ongoing and the resulting model forms part of the same planned research programme. No patient-level data or "
        "private credentials are included. Users may reproduce the disclosed workflow with a legally obtained local base model and their own authorized "
        "data; reasonable requests concerning derived data may be directed to hangcao87@163.com, subject to source licences, author approval and applicable "
        "institutional requirements."
    )
    old_release = "The model weights and training code will be released openly."
    new_release = (
        "The data-processing, training and evaluation code is available at https://github.com/hangcao87/FractureAgent; trained model weights and LoRA "
        "checkpoints are not publicly released because follow-on validation, intellectual-property assessment and planned grant-supported work are ongoing."
    )

    with zipfile.ZipFile(args.input_docx, "r") as source:
        document = etree.fromstring(source.read("word/document.xml"))
        settings = etree.fromstring(source.read("word/settings.xml"))
        revision_nodes = document.xpath(
            ".//w:ins|.//w:del|.//w:moveTo|.//w:moveFrom|.//w:pPrChange|.//w:rPrChange|"
            ".//w:tblPrChange|.//w:trPrChange|.//w:tcPrChange|.//w:sectPrChange|.//w:numberingChange|"
            ".//w:cellIns|.//w:cellDel|.//w:cellMerge",
            namespaces=NS,
        )
        if revision_nodes:
            raise RuntimeError("Input contains tracked revisions; accept prior-round changes before building this revision")
        paragraphs = document.xpath(".//w:body/w:p", namespaces=NS)
        change_id = next_change_id(document)

        def find(prefix: str, last: bool = False):
            matches = [p for p in paragraphs if local_text(p).startswith(prefix)]
            return matches[-1] if last and matches else (matches[0] if matches else None)

        affiliation_paragraph = find("c Department of Orthopedics, Xuzhou New Health Hospital")
        if affiliation_paragraph is None:
            raise RuntimeError("Cannot find the third affiliation")
        change_id = replace_after_first_run(affiliation_paragraph, affiliation, change_id, args.author)

        for prefix, text in [("Background.", abstract), ("Methods.", ""), ("Results.", ""), ("Conclusions.", "")]:
            paragraph = find(prefix)
            if paragraph is None:
                raise RuntimeError(f"Cannot find abstract paragraph: {prefix}")
            change_id = replace_paragraph(paragraph, text, change_id, args.author)

        conclusion_paragraph = find("Single-GPU training recipe", last=True)
        if conclusion_paragraph is None:
            raise RuntimeError("Cannot find the conclusion training-recipe paragraph")
        change_id = replace_substring(conclusion_paragraph, old_release, new_release, change_id, args.author)

        data_paragraph = find("Availability of data and materials.")
        if data_paragraph is None:
            raise RuntimeError("Cannot find the data availability paragraph")
        change_id = insert_paragraph_after(data_paragraph, code_text, change_id, args.author)

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
