#!/usr/bin/env python
"""Build the final Word report for the BIC/qBIC database project."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Inches, Pt, RGBColor


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB = PROJECT_DIR / "data" / "bic_literature_verified.sqlite"
DEFAULT_OUT = PROJECT_DIR / "outputs" / "BIC_qBIC_verified_database_research_report.docx"


def add_heading(doc: Document, text: str, level: int = 1) -> None:
    doc.add_heading(text, level=level)


def add_table(doc: Document, headers: list[str], rows: list[list[object]], widths: list[float] | None = None) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        hdr[i].paragraphs[0].runs[0].font.bold = True
        hdr[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        hdr[i]._tc.get_or_add_tcPr().append(parse_shd("1F4E78"))
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            text = str(value or "")
            if len(text) > 450:
                text = text[:450] + "..."
            cells[i].text = text
            cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
    if widths:
        for row in table.rows:
            for idx, width in enumerate(widths):
                row.cells[idx].width = Inches(width)
    doc.add_paragraph()


def parse_shd(fill: str):
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    return shd


def bullet(doc: Document, text: str) -> None:
    doc.add_paragraph(text, style="List Bullet")


def numbered(doc: Document, text: str) -> None:
    doc.add_paragraph(text, style="List Number")


def rows(conn: sqlite3.Connection, query: str) -> list[sqlite3.Row]:
    return list(conn.execute(query).fetchall())


def build(db_path: Path, out_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Inches(0.8)
    sec.bottom_margin = Inches(0.8)
    sec.left_margin = Inches(0.8)
    sec.right_margin = Inches(0.8)

    styles = doc.styles
    styles["Normal"].font.name = "Calibri"
    styles["Normal"].font.size = Pt(10.5)
    for name in ["Heading 1", "Heading 2", "Heading 3"]:
        styles[name].font.name = "Calibri"
        styles[name].font.color.rgb = RGBColor(31, 78, 121)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("BIC/qBIC Verified Physical-Results Database and Research Ideas")
    run.bold = True
    run.font.size = Pt(18)
    run.font.color.rgb = RGBColor(15, 55, 90)
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.add_run("Source-traceable literature database, review workbook, and physics-driven research directions").italic = True
    doc.add_paragraph()

    total_papers = conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
    total_obs = conn.execute("SELECT COUNT(*) FROM physical_observations").fetchone()[0]
    local_obs = conn.execute("SELECT COUNT(*) FROM physical_observations WHERE source_kind='local_pdf_text'").fetchone()[0]
    web_obs = conn.execute("SELECT COUNT(*) FROM physical_observations WHERE source_kind='web_article_text'").fetchone()[0]
    core = conn.execute("SELECT COUNT(*) FROM papers WHERE verification_status='manual_pdf_verified_core'").fetchone()[0]
    ext = conn.execute("SELECT COUNT(*) FROM external_verified_papers").fetchone()[0]

    add_heading(doc, "Executive Conclusion", 1)
    doc.add_paragraph(
        "The project has moved from a bibliography-only seed into a physics-results database architecture. "
        "The current database indexes 50 local BIC/qBIC PDFs, promotes 13 core papers after local PDF quote/id checks, "
        f"and stores {total_obs} source-quoted physical observation rows. These rows cover structure, materials, Q, wavelength/frequency, "
        "Fano/linewidth, spectra, k-space, band-structure, and polarization/topology language. Most rows are deliberately marked as review queues rather than final facts."
    )
    bullet(doc, f"Local PDFs indexed: {total_papers}")
    bullet(doc, f"Core bibliography records manually promoted: {core}")
    bullet(doc, f"Physical observation candidates from local PDFs: {local_obs}")
    bullet(doc, f"Physical observations added from web article text: {web_obs}")
    bullet(doc, f"External prior-art / web source records: {ext}")

    add_heading(doc, "Data Integrity Boundary", 1)
    doc.add_paragraph(
        "The database uses a conservative rule: metadata can be paper-level, but physics must be evidence-level. "
        "Q factors, resonance wavelengths, Fano parameters, geometry dimensions, band structures, k-space features, and polarization/topology claims must be linked to source quote, page/figure/table where available, and verification status. "
        "Rows marked candidate_needs_review are real-source extraction candidates, not final curated facts."
    )
    numbered(doc, "Automatic regex extraction creates review queues only.")
    numbered(doc, "Web article text observations carry source URLs and quotes but still need secondary review for publication-grade use.")
    numbered(doc, "No synthetic/proxy data is mixed into the verified database.")
    numbered(doc, "Excel is the human review surface; SQLite is the durable structured backend.")

    add_heading(doc, "Database and Workbook Deliverables", 1)
    add_table(
        doc,
        ["Artifact", "Path", "Purpose"],
        [
            ["SQLite database", str(PROJECT_DIR / "data" / "bic_literature_verified.sqlite"), "Durable relational database with evidence and observation tables."],
            ["Excel review workbook", str(PROJECT_DIR / "outputs" / "BIC_verified_database_review.xlsx"), "Convenient manual filtering and review of observations."],
            ["Verified CSV exports", str(PROJECT_DIR / "exports_verified"), "Plain-table exports for independent inspection."],
            ["Sandbox", str(PROJECT_DIR / "sandbox_non_database"), "Synthetic/proxy pipeline kept separate from real literature data."],
        ],
        [1.4, 3.2, 2.0],
    )

    add_heading(doc, "Physical Observation Coverage", 1)
    obs_rows = rows(
        conn,
        """
        SELECT source_kind, observation_type, COUNT(*) n
        FROM physical_observations
        GROUP BY source_kind, observation_type
        ORDER BY source_kind, n DESC
        """,
    )
    add_table(doc, ["Source", "Observation type", "Rows"], [[r["source_kind"], r["observation_type"], r["n"]] for r in obs_rows], [1.8, 2.8, 0.8])

    add_heading(doc, "Examples of Web-Added Physical Results", 1)
    web_rows = rows(
        conn,
        """
        SELECT quantity_name, value_text, quote, source_url
        FROM physical_observations
        WHERE source_kind='web_article_text'
        ORDER BY source_url, observation_id
        LIMIT 12
        """,
    )
    add_table(doc, ["Quantity", "Value", "Source quote", "URL"], [[r["quantity_name"], r["value_text"], r["quote"], r["source_url"]] for r in web_rows], [1.3, 1.2, 3.0, 1.6])

    add_heading(doc, "Novelty Risks", 1)
    ext_rows = rows(
        conn,
        """
        SELECT title, year, source, doi, overlap_risk, notes
        FROM external_verified_papers
        WHERE overlap_risk IN ('very_high','high','high_adjacent')
        ORDER BY CASE overlap_risk WHEN 'very_high' THEN 0 WHEN 'high' THEN 1 ELSE 2 END, year
        LIMIT 10
        """,
    )
    add_table(doc, ["Prior work", "Year", "Source", "DOI", "Risk", "Blocked claim"], [[r["title"], r["year"], r["source"], r["doi"], r["overlap_risk"], r["notes"]] for r in ext_rows], [2.0, 0.5, 1.1, 1.1, 0.8, 2.2])

    add_heading(doc, "Research Ideas", 1)
    add_heading(doc, "Idea 1: Fourier Harmonics to TCMT Radiative-Coupling Causality", 2)
    doc.add_paragraph(
        "Core question: Which Fourier components of the 2D dielectric distribution control radiative leakage gamma_rad, Fano q, resonance zero/pole positions, and far-field polarization vortex structure? "
        "The proposed experiment is causal: delete, inject, or phase-flip selected Fourier shells or symmetry channels, reconstruct a physically valid geometry, rerun full-wave simulation, and fit TCMT/Fano parameters."
    )
    bullet(doc, "Data required: eps2d, raw/delta FFT, complex transmission/reflection, angle-resolved spectra, polarization maps, TCMT/Fano fits.")
    bullet(doc, "Novelty guard: do not frame this as ML prediction; frame it as Fourier-channel causality for qBIC radiation coupling.")
    bullet(doc, "Immediate contribution possible now: use the database to map which papers provide Q/Fano/k-space/polarization data needed for this causal atlas.")

    add_heading(doc, "Idea 2: Topological-Charge-Aware Finite-Size/Loss/Q-Scaling Phase Diagram", 2)
    doc.add_paragraph(
        "Core question: Where and why does the common Q proportional to alpha^-2 law fail? "
        "Model the observed Q as a loss decomposition: 1/Q = 1/Q_rad(alpha,N,charge) + 1/Q_abs + 1/Q_edge + 1/Q_disorder. "
        "The novelty is combining topology charge or BIC merging state with finite array size, material loss, substrate leakage, and roughness spectra."
    )
    bullet(doc, "Data required: asymmetry alpha, array size N, material k, substrate, reported/measured Q, polarization vortex or charge, and spectrum fit method.")
    bullet(doc, "Database role: physical_observations already identifies Q/scaling/k-space candidates; next step is human promotion of rows to verified facts.")

    add_heading(doc, "Idea 3: Fourier-Disorder Engineering of Roughness-Induced qBIC Leakage", 2)
    doc.add_paragraph(
        "Core question: Does qBIC degradation depend only on roughness RMS, or on specific disorder Fourier bands? "
        "Treat fabrication disorder as a spectral perturbation to the dielectric boundary, connect it to TCMT loss channels, and test topological-vortex robustness under controlled roughness spectra."
    )

    add_heading(doc, "Recommended Next Actions", 1)
    numbered(doc, "Open the Excel workbook and filter Physical_Observations by observation_type = q_factor, wavelength, frequency, fano_parameter, k_space, band_structure, and polarization.")
    numbered(doc, "Promote only rows with clear source quote and sufficient context; reject reference-list false positives and generic mentions.")
    numbered(doc, "For the top 20 web/PDF sources, download supplementary/source data where available before digitizing figures.")
    numbered(doc, "Create HDF5 arrays only after physical rows are verified and linked to a device/structure record.")
    numbered(doc, "Use Idea 1 and Idea 2 as the main research thrust; keep Idea 3 as a second-stage experimental/statistical extension.")

    doc.add_page_break()
    add_heading(doc, "Appendix: Core Verified Bibliography", 1)
    core_rows = rows(
        conn,
        """
        SELECT p.title, p.year, p.source, p.doi, p.arxiv
        FROM papers p
        WHERE p.verification_status='manual_pdf_verified_core'
        ORDER BY p.year, p.title
        """,
    )
    add_table(doc, ["Title", "Year", "Source", "DOI", "arXiv"], [[r["title"], r["year"], r["source"], r["doi"], r["arxiv"]] for r in core_rows], [3.0, 0.5, 1.2, 1.3, 0.8])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out_path)
    conn.close()
    print(f"Wrote Word report: {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    build(args.db, args.out)


if __name__ == "__main__":
    main()
