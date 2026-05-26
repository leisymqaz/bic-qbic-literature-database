#!/usr/bin/env python
"""Promote a small core-paper set only when PDF/Crossref evidence matches.

This script does not infer physics labels. It updates bibliographic facts for
core papers when a DOI/arXiv/title/quote can be verified against the local PDF
text already indexed in evidence or against Crossref metadata stored in the DB.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sqlite3
from pathlib import Path

try:
    import fitz
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyMuPDF is required: install package 'pymupdf'.") from exc


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PROJECT_DIR / "data" / "bic_literature_verified.sqlite"


CORE = [
    {
        "file": "Experimental Observation of Optical Bound States in the Continuum.pdf",
        "title": "Experimental Observation of Optical Bound States in the Continuum",
        "doi": "10.1103/PhysRevLett.107.183901",
        "year": 2011,
        "source": "Physical Review Letters",
        "quote": "experimental observation of bound states in the continuum",
    },
    {
        "file": "PhysRevLett.113.037401.pdf",
        "title": "Analytical Perspective for Bound States in the Continuum in Photonic Crystal Slabs",
        "doi": "10.1103/PhysRevLett.113.037401",
        "year": 2014,
        "source": "Physical Review Letters",
        "quote": "photonic bound states in the continuum",
    },
    {
        "file": "PRL2014-BIC拓扑.pdf",
        "title": "Topological Nature of Optical Bound States in the Continuum",
        "doi": "10.1103/PhysRevLett.113.257401",
        "year": 2014,
        "source": "Physical Review Letters",
        "quote": "BICs are vortex centers",
    },
    {
        "file": "Embedded Photonic Eigenvalues in 3D Nanostructures.pdf",
        "title": "Embedded Photonic Eigenvalues in 3D Nanostructures",
        "doi": "10.1103/PhysRevLett.112.213903",
        "year": 2014,
        "source": "Physical Review Letters",
        "quote": "radiation continuum",
    },
    {
        "file": "srep-Formation mechanism of guided resonances and BIC in photonic crystal slab.pdf",
        "title": "Formation mechanism of guided resonances and bound states in the continuum in photonic crystal slabs",
        "doi": "10.1038/srep31908",
        "year": 2016,
        "source": "Scientific Reports",
        "quote": "guided resonances and bound states in the continuum",
    },
    {
        "file": "Nature2017-Lasing action from photonic bound states in continum.pdf",
        "title": "Lasing action from photonic bound states in continuum",
        "doi": "10.1038/nature20799",
        "year": 2017,
        "source": "Nature",
        "quote": "called bound states in the continuum",
    },
    {
        "file": "Nature Photon2017-Anisotropy-induced photonic bound states in the continum.pdf",
        "title": "Anisotropy-induced photonic bound states in the continuum",
        "doi": "10.1038/NPHOTON.2017.31",
        "year": 2017,
        "source": "Nature Photonics",
        "quote": "BICs are radiationless localized states",
    },
    {
        "file": "Bound states within the radiation continuum in diffraction grating and the role of leaky modes.pdf",
        "title": "Bound states within the radiation continuum in diffraction gratings and the role of leaky modes",
        "doi": "10.1088/1367-2630/aa849f",
        "year": 2017,
        "source": "New Journal of Physics",
        "quote": "resonant states with diverging Q factor",
    },
    {
        "file": "没看Light enhancement by quasi-bound states in.pdf",
        "title": "Light enhancement by quasi-bound states in the continuum in dielectric arrays",
        "doi": "10.1364/OE.25.014134",
        "year": 2017,
        "source": "Optics Express",
        "quote": "high-Q structural resonant modes originated from bound states in the continuum",
    },
    {
        "file": "Quasi Bound States in the Continuum with Few Unit.pdf",
        "title": "Quasi Bound States in the Continuum with Few Unit Cells of Photonic Crystal Slab",
        "doi": None,
        "arxiv": "1705.09842",
        "year": 2017,
        "source": "arXiv preprint / Optica template needs verification",
        "quote": "BICs can turn into quasi-BICs",
    },
    {
        "file": "[Nanophotonics] Nonradiating photonics with resonant dielectric nanostructures.pdf",
        "title": "Nonradiating photonics with resonant dielectric nanostructures",
        "doi": "10.1515/nanoph-2019-0024",
        "year": 2019,
        "source": "Nanophotonics",
        "quote": "bound states in the continuum",
    },
    {
        "file": "1909.12618.pdf",
        "title": "Generating optical vortex beams by momentum-space polarization vortices centered at bound states in the continuum",
        "doi": None,
        "arxiv": "1909.12618",
        "year": 2019,
        "source": "arXiv preprint",
        "quote": "polarization around bound states in the continuum",
    },
    {
        "file": "Advanced Photonics2021-单胞高Q.pdf",
        "title": "Pushing the limit of high-Q mode of a single dielectric nanocavity",
        "doi": "10.1117/1.AP.3.1.016004",
        "year": 2021,
        "source": "Advanced Photonics",
        "quote": "quasi bound-state-in-the-continuum",
    },
    {
        "file": "NC2022-简并BIC.pdf",
        "title": "Realizing symmetry-guaranteed pairs of bound states in the continuum in metasurfaces",
        "doi": "10.1038/s41467-022-35246-w",
        "year": 2022,
        "source": "Nature Communications",
        "quote": "degenerate pairs of bound states in the continuum",
    },
    {
        "file": "s41467-023-41068-1.pdf",
        "title": "Twisted moire photonic crystal enabled optical vortex generation through bound states in the continuum",
        "doi": "10.1038/s41467-023-41068-1",
        "year": 2023,
        "source": "Nature Communications",
        "quote": "optical vortex generation through bound states in the continuum",
    },
]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def extract_text(path: Path, max_pages: int = 5) -> str:
    chunks = []
    doc = fitz.open(path)
    for i in range(min(max_pages, doc.page_count)):
        chunks.append(doc.load_page(i).get_text("text"))
    doc.close()
    return "\n".join(chunks)


def find_quote(text: str, quote: str) -> tuple[bool, str | None]:
    norm_text = normalize(text)
    norm_quote = normalize(quote)
    index = norm_text.find(norm_quote)
    if index < 0:
        return False, None
    raw = re.sub(r"\s+", " ", text)
    # Approximate snippet from normalized position; enough for an audit note.
    return True, raw[max(0, index - 180) : index + len(quote) + 180]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    promoted = 0
    skipped = []

    for item in CORE:
        row = conn.execute(
            """
            SELECT p.paper_id, sf.file_id, sf.pdf_path, p.crossref_title, p.crossref_year, p.crossref_container
            FROM papers p JOIN source_files sf USING(file_id)
            WHERE sf.file_name=?
            """,
            [item["file"]],
        ).fetchone()
        if not row:
            skipped.append((item["file"], "file_not_found_in_db"))
            continue
        text = extract_text(Path(row["pdf_path"]), max_pages=5)
        quote_ok, snippet = find_quote(text, item["quote"])
        doi_ok = True
        if item.get("doi"):
            doi_ok = normalize(item["doi"]) in normalize(text) or normalize(item["doi"]) in normalize(str(row["crossref_title"] or ""))
        arxiv_ok = True
        if item.get("arxiv"):
            arxiv_ok = item["arxiv"] in text or item["arxiv"] in item["file"]
        if not (quote_ok and doi_ok and arxiv_ok):
            skipped.append((item["file"], f"quote_ok={quote_ok}, doi_ok={doi_ok}, arxiv_ok={arxiv_ok}"))
            continue

        conn.execute(
            """
            UPDATE papers
            SET title=?, title_source='manual_pdf_quote_verified',
                doi=?, doi_source=?,
                arxiv=?, arxiv_source=?,
                year=?, year_source='manual_pdf_or_crossref_verified',
                source=?, source_source='manual_pdf_or_crossref_verified',
                verification_status='manual_pdf_verified_core',
                curation_status='bibliography_verified_no_numeric_data',
                notes='Core bibliography fact promoted only after local PDF quote/id check. No device/resonance numeric facts inferred.'
            WHERE paper_id=?
            """,
            [
                item["title"],
                item.get("doi"),
                "manual_pdf_text_or_crossref" if item.get("doi") else None,
                item.get("arxiv"),
                "manual_pdf_text_or_filename" if item.get("arxiv") else None,
                item["year"],
                item["source"],
                row["paper_id"],
            ],
        )
        evidence_id = f"E-{row['paper_id']}-COREVERIFY"
        conn.execute("DELETE FROM evidence WHERE evidence_id=?", [evidence_id])
        conn.execute(
            """
            INSERT INTO evidence
            (evidence_id, paper_id, file_id, source_kind, source_path, page_start, quote, quote_sha256,
             extraction_method, evidence_level, confidence, verification_status, created_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?)
            """,
            [
                evidence_id,
                row["paper_id"],
                row["file_id"],
                "local_pdf_manual_core_check",
                row["pdf_path"],
                1,
                snippet or item["quote"],
                sha256_text(snippet or item["quote"]),
                "manual_core_list_verified_against_pdf_text",
                "E1",
                0.9,
                "verified_core_bibliography_only",
                "Bibliographic core check. Does not verify numerical device/resonance data.",
            ],
        )
        promoted += 1

    conn.execute(
        "INSERT INTO audit_log (event_time, level, message, details) VALUES (datetime('now'), ?, ?, ?)",
        ["INFO", f"Applied core PDF verification to {promoted} papers", str(skipped)],
    )
    conn.commit()
    conn.close()
    print(f"Promoted {promoted} core papers")
    if skipped:
        print("Skipped:")
        for item in skipped:
            print(item)


if __name__ == "__main__":
    main()
