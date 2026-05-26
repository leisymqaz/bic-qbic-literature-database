#!/usr/bin/env python
"""Extract source-quoted physical observations from local BIC PDFs.

The output is a review queue, not final verified physics. Each row includes a
quote and location so it can be audited and promoted later.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

try:
    import fitz
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyMuPDF is required: install package 'pymupdf'.") from exc


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PROJECT_DIR / "data" / "bic_literature_verified.sqlite"


@dataclass
class PatternSpec:
    observation_group: str
    observation_type: str
    quantity_name: str
    regex: re.Pattern[str]
    confidence: float


PATTERNS = [
    PatternSpec("resonance", "q_factor", "Q factor", re.compile(r"\bQ(?:[-\s]?factor)?\s*(?:of|=|~|≈|>|<|up to|as high as|reaches|exceeding)?\s*(?:about|around)?\s*([0-9][0-9,]*(?:\.[0-9]+)?(?:\s*[x×]\s*10\^?\s*[0-9]+|e[+\-]?[0-9]+)?)", re.I), 0.62),
    PatternSpec("resonance", "wavelength", "resonance wavelength", re.compile(r"\b(?:resonance|resonant|peak|dip|mode)?\s*(?:wavelength|lambda|λ)\s*(?:of|=|~|≈|at|around|near)?\s*([0-9]{2,5}(?:\.[0-9]+)?)\s*(nm|µm|um|μm|micron)", re.I), 0.60),
    PatternSpec("resonance", "frequency", "resonance frequency", re.compile(r"\b(?:frequency|freq\.?|resonance)\s*(?:of|=|~|≈|at|around|near)?\s*([0-9]+(?:\.[0-9]+)?)\s*(THz|GHz|cm\^-1|cm−1)", re.I), 0.58),
    PatternSpec("resonance", "fano_parameter", "Fano q", re.compile(r"\bFano\s*(?:parameter|asymmetry parameter)?\s*q\s*(?:=|~|≈)?\s*([+\-]?[0-9]+(?:\.[0-9]+)?)", re.I), 0.65),
    PatternSpec("resonance", "linewidth", "linewidth", re.compile(r"\b(?:linewidth|line width|FWHM|width)\s*(?:of|=|~|≈)?\s*([0-9]+(?:\.[0-9]+)?)\s*(nm|meV|GHz|THz|cm\^-1|cm−1)", re.I), 0.58),
    PatternSpec("structure", "period", "period/lattice constant", re.compile(r"\b(?:period|periodicity|lattice constant|pitch)\s*(?:a)?\s*(?:=|~|≈|of)?\s*([0-9]+(?:\.[0-9]+)?)\s*(nm|µm|um|μm)", re.I), 0.60),
    PatternSpec("structure", "thickness", "thickness/height", re.compile(r"\b(?:thickness|height|depth)\s*(?:h)?\s*(?:=|~|≈|of)?\s*([0-9]+(?:\.[0-9]+)?)\s*(nm|µm|um|μm)", re.I), 0.58),
    PatternSpec("structure", "radius", "radius", re.compile(r"\b(?:radius|r)\s*(?:=|~|≈|of)?\s*([0-9]+(?:\.[0-9]+)?)\s*(nm|µm|um|μm)", re.I), 0.48),
    PatternSpec("structure", "diameter", "diameter", re.compile(r"\b(?:diameter|width|length|gap)\s*(?:=|~|≈|of)?\s*([0-9]+(?:\.[0-9]+)?)\s*(nm|µm|um|μm)", re.I), 0.45),
    PatternSpec("material", "material", "material", re.compile(r"\b(?:silicon|Si|GaAs|AlGaAs|TiO2|titanium dioxide|SiN|Si3N4|silica|SiO2|perovskite|InGaN|AlxGa1|dielectric|gold|silver)\b", re.I), 0.42),
    PatternSpec("kspace", "k_space", "k-space / momentum-space", re.compile(r"\b(?:k[-\s]?space|momentum[-\s]?space|Brillouin zone|Γ point|Gamma point|polarization vortex|topological charge|Poincar[eé] index)\b", re.I), 0.50),
    PatternSpec("band", "band_structure", "band structure", re.compile(r"\b(?:band structure|dispersion|light cone|radiation continuum|leaky mode|Bloch mode)\b", re.I), 0.48),
    PatternSpec("spectrum", "spectrum", "spectrum", re.compile(r"\b(?:transmission spectrum|reflection spectrum|reflectance|transmittance|absorption spectrum|photoluminescence|far[-\s]?field)\b", re.I), 0.48),
    PatternSpec("polarization", "polarization", "polarization/topology", re.compile(r"\b(?:polarization|circular dichroism|chiral|handedness|Stokes|vortex beam|optical vortex|topological charge)\b", re.I), 0.46),
]


def clean(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:16]


def numeric_value(raw: str | None) -> float | None:
    if not raw:
        return None
    s = raw.replace(",", "").replace("×", "x").strip()
    sci = re.match(r"([0-9]+(?:\.[0-9]+)?)\s*x\s*10\^?\s*([0-9]+)", s, re.I)
    if sci:
        return float(sci.group(1)) * (10 ** int(sci.group(2)))
    try:
        return float(re.sub(r"[^0-9eE+\-.]", "", s))
    except ValueError:
        return None


def wavelength_nm(value: float | None, unit: str | None) -> float | None:
    if value is None or unit is None:
        return None
    u = unit.lower()
    if u == "nm":
        return value
    if u in {"µm", "um", "μm", "micron"}:
        return value * 1000.0
    return None


def extract_pages(path: Path, max_pages: int | None) -> list[str]:
    doc = fitz.open(path)
    limit = doc.page_count if max_pages is None else min(max_pages, doc.page_count)
    pages = [clean(doc.load_page(i).get_text("text")) for i in range(limit)]
    doc.close()
    return pages


def surrounding(text: str, start: int, end: int, window: int = 260) -> str:
    return clean(text[max(0, start - window) : min(len(text), end + window)])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--max-pages", type=int, default=8)
    parser.add_argument("--max-per-paper-type", type=int, default=8)
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    conn.execute("DELETE FROM physical_observations WHERE source_kind='local_pdf_text'")

    papers = conn.execute(
        """
        SELECT p.paper_id, sf.file_id, sf.pdf_path
        FROM papers p JOIN source_files sf USING(file_id)
        ORDER BY p.paper_id
        """
    ).fetchall()
    inserted = 0
    for paper in papers:
        path = Path(paper["pdf_path"])
        try:
            pages = extract_pages(path, args.max_pages)
        except Exception:
            continue
        per_type_counts: dict[str, int] = {}
        for page_index, page_text in enumerate(pages, start=1):
            for spec in PATTERNS:
                if per_type_counts.get(spec.observation_type, 0) >= args.max_per_paper_type:
                    continue
                for match in spec.regex.finditer(page_text):
                    if per_type_counts.get(spec.observation_type, 0) >= args.max_per_paper_type:
                        break
                    quote = surrounding(page_text, match.start(), match.end())
                    raw_value = match.group(1) if match.lastindex and match.lastindex >= 1 else match.group(0)
                    unit = match.group(2) if match.lastindex and match.lastindex >= 2 else None
                    val = numeric_value(raw_value)
                    obs_id = f"OBS-{paper['paper_id']}-{spec.observation_type}-{page_index}-{sha(quote)}"
                    ev_id = f"E-{obs_id}"
                    conn.execute("DELETE FROM evidence WHERE evidence_id=?", [ev_id])
                    conn.execute(
                        """
                        INSERT INTO evidence
                        (evidence_id, paper_id, file_id, source_kind, source_path, page_start, page_end, quote,
                         quote_sha256, extraction_method, evidence_level, confidence, verification_status, created_at, notes)
                        VALUES (?, ?, ?, 'local_pdf_text_observation', ?, ?, ?, ?, ?, ?, 'E0', ?, 'candidate_needs_review',
                                datetime('now'), ?)
                        """,
                        [
                            ev_id,
                            paper["paper_id"],
                            paper["file_id"],
                            str(path),
                            page_index,
                            page_index,
                            quote,
                            hashlib.sha256(quote.encode("utf-8", errors="ignore")).hexdigest(),
                            f"regex:{spec.observation_type}",
                            spec.confidence,
                            "Automatically extracted observation candidate. Verify against PDF before using as fact.",
                        ],
                    )
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO physical_observations
                        (observation_id, paper_id, file_id, observation_group, observation_type, quantity_name,
                         value_text, value_numeric, unit, wavelength_nm, q_factor, fano_q,
                         source_kind, page, quote, evidence_id, extraction_method, verification_status,
                         curation_status, confidence, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'local_pdf_text', ?, ?, ?, ?, 'candidate_needs_review',
                                'review_queue', ?, ?)
                        """,
                        [
                            obs_id,
                            paper["paper_id"],
                            paper["file_id"],
                            spec.observation_group,
                            spec.observation_type,
                            spec.quantity_name,
                            raw_value,
                            val,
                            unit,
                            wavelength_nm(val, unit),
                            val if spec.observation_type == "q_factor" else None,
                            val if spec.observation_type == "fano_parameter" else None,
                            page_index,
                            quote,
                            ev_id,
                            f"regex:{spec.observation_type}",
                            spec.confidence,
                            "Candidate physical observation from PDF text; not yet human verified.",
                        ],
                    )
                    per_type_counts[spec.observation_type] = per_type_counts.get(spec.observation_type, 0) + 1
                    inserted += 1

    conn.execute(
        "INSERT INTO audit_log (event_time, level, message, details) VALUES (datetime('now'), 'INFO', ?, ?)",
        ["Extracted local physical observation candidates", f"inserted={inserted}, max_pages={args.max_pages}"],
    )
    conn.commit()
    conn.close()
    print(f"Inserted {inserted} local physical observation candidates")


if __name__ == "__main__":
    main()
