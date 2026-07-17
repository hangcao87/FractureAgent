"""Build a formatted DOCX point-by-point response from the repository markdown text."""
from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from docx.oxml.ns import qn


BLUE = RGBColor(31, 78, 121)
RED = RGBColor(192, 0, 0)


def set_font(run, name="Arial", size=10.5, bold=False, italic=False, color=None):
    run.font.name = name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color


def add_para(doc, text="", style=None, before=0, after=6, line=1.08):
    p = doc.add_paragraph(style=style)
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = line
    if text:
        r = p.add_run(text)
        set_font(r)
    return p


def add_labelled(doc, label, text, color=BLUE, italic=False):
    p = add_para(doc, after=6)
    r = p.add_run(label)
    set_font(r, bold=True, italic=italic, color=color)
    r = p.add_run(text)
    set_font(r, italic=italic, color=color)
    return p


def build(out: str):
    root = Path(__file__).resolve().parents[1]
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.72)
    section.bottom_margin = Inches(0.72)
    section.left_margin = Inches(0.85)
    section.right_margin = Inches(0.85)
    styles = doc.styles
    styles["Normal"].font.name = "Arial"
    styles["Normal"]._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    styles["Normal"]._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    styles["Normal"].font.size = Pt(10.5)

    p = add_para(doc, before=0, after=3)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Point-by-Point Response to Reviewers")
    set_font(r, size=16, bold=True, color=BLUE)
    p = add_para(doc, before=0, after=3)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("FractureAgent: A Multi-Tool LLM-Based Intelligent Agent for Personalized Fracture Rehabilitation Management")
    set_font(r, size=11.5, bold=True)
    p = add_para(doc, before=0, after=12)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Journal: Scientific Reports    Decision: Minor Revision    Manuscript ID: 0d10e894-9f9f-41a6-9d8e-f7f456b33960")
    set_font(r, size=9, color=BLUE)
    add_para(doc, "Dear Editor and Reviewers,", after=8)
    intro = "We sincerely thank the Editor and the Reviewers for their careful assessment and constructive suggestions. We have revised the manuscript and the accompanying research repository to improve abstract readability, code transparency and reproducibility. The revised manuscript is supplied as a tracked-change file. Our point-by-point responses are provided below."
    add_para(doc, intro, after=10)

    add_labelled(doc, "Response to Reviewer 1", "", color=BLUE)
    add_labelled(doc, "Reviewer comment: ", "Thank you.", color=BLUE, italic=True)
    add_labelled(doc, "Response: ", "We thank the Reviewer for the positive assessment. We have nevertheless made the cross-cutting transparency revision requested in this round, including the unstructured abstract and the dedicated Code Availability statement.")

    add_labelled(doc, "Response to Reviewer 2", "", color=BLUE)
    add_labelled(doc, "Reviewer comment: ", "The authors have matched all the previously highlighted points. Hence, it is now worthy of publication and I hope it will reach the widest audience possible. https://github.com/hangcao87/FractureAgent", color=BLUE, italic=True)
    add_labelled(doc, "Response: ", "We sincerely thank the Reviewer for the positive assessment and for recognizing the revisions made in the previous round. We have continued to improve the accompanying repository. The public main branch contains the complete data-processing code, versioned prompts, tool schemas and implementations, deterministic safety gate, ms-swift/Swift QLoRA training configuration and launchers, evaluation code, and non-sensitive reproducibility-record templates. The training data and trained model weights are not included. The repository is available at https://github.com/hangcao87/FractureAgent.")

    doc.add_page_break()
    add_labelled(doc, "Response to Reviewer 4", "", color=BLUE)
    add_labelled(doc, "Comment 4.1 - Reviewer comment: ", "The abstract would benefit from revision to better align with the journal's format and improve readability. The current abstract is structured using subheadings (Background, Methods, Results, Conclusions) and is relatively lengthy. Consider converting it into a single unstructured paragraph and reducing its length by focusing on the most essential methodological details and key findings.", color=BLUE, italic=True)
    add_labelled(doc, "Response: ", "We agree with the Reviewer. We replaced the structured abstract with a single unstructured paragraph and shortened it by retaining only the study rationale, the FractureAgent architecture, the essential training and evaluation design, the principal findings and the simulation-based limitation.")
    add_labelled(doc, "Manuscript location: ", "Abstract.", color=RED)
    add_labelled(doc, "Comment 4.2 - Reviewer comment: ", "To enhance transparency and reproducibility, please consider adding a dedicated Code Availability statement. The manuscript provides substantial methodological detail; however, it is currently unclear whether the source code, training scripts, tool implementations, prompts, or model checkpoints are publicly available. If these resources cannot be shared, the authors should explicitly state this and provide the reason.", color=BLUE, italic=True)
    add_labelled(doc, "Response: ", "We agree that a dedicated statement is needed. We added a separate Code Availability paragraph under Declarations. The public repository contains the data-processing scripts, versioned training prompts, tool schemas and implementations, the deterministic safety gate, the ms-swift/Swift QLoRA configuration and launchers, evaluation code and non-sensitive run-record templates. The trained model weights, LoRA checkpoints, private credentials and the curated training corpus are not publicly released at this stage because they are being retained for ongoing research, intellectual-property protection and grant-related work. No patient-level data are distributed. Reasonable requests concerning derived data may be directed to hangcao87@163.com, subject to source licences, author approval and applicable institutional requirements.")
    add_labelled(doc, "Manuscript location: ", "Declarations, Code availability; Availability of data and materials; Section 8, Conclusion.", color=RED)

    add_labelled(doc, "Manuscript change checklist", "", color=BLUE)
    for item in [
        "Abstract: converted the structured Background/Methods/Results/Conclusions format into one unstructured paragraph.",
        "Declarations: stated that the curated training corpus is not publicly distributed and added the derived-data request route.",
        "Declarations: added a dedicated Code Availability statement covering data processing, prompts, tools, Swift training, evaluation and run records.",
        "Conclusion: removed the inconsistent statement that model weights would be released openly.",
        "Repository: added Swift-only installation, data export, QLoRA SFT, inference, evaluation and run-record workflows; no training data or checkpoints were added.",
    ]:
        p = add_para(doc, after=3)
        r = p.add_run("- " + item)
        set_font(r)
    add_labelled(doc, "Missing information / risk flags: ", "None for the supplied comments. Before submission, confirm that the journal permits the stated access-request route and that the public branch contains the files listed above.")
    add_para(doc, "Sincerely,", before=12, after=3)
    add_para(doc, "Dr Xiao Ouyang and Dr Weijuan Gong", after=2)
    add_para(doc, "Corresponding authors, on behalf of all authors", after=0)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    doc.save(out)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    build(ap.parse_args().out)
