#!/usr/bin/env python
"""Generate a concise Markdown report from the BIC literature database."""

from __future__ import annotations

import argparse
import sqlite3
from collections import Counter
from datetime import datetime
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PROJECT_DIR / "data" / "bic_literature.sqlite"
DEFAULT_REPORT_PATH = PROJECT_DIR / "reports" / "bic_literature_database_initial_report.md"


def scalar(conn: sqlite3.Connection, query: str, params: tuple = ()) -> int:
    return int(conn.execute(query, params).fetchone()[0])


def rows(conn: sqlite3.Connection, query: str, params: tuple = ()) -> list[sqlite3.Row]:
    return list(conn.execute(query, params).fetchall())


def md_table(headers: list[str], data: list[list[object]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in data:
        cells = [str(cell if cell is not None else "").replace("\n", " ").strip() for cell in row]
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def generate(db_path: Path, report_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    total = scalar(conn, "SELECT COUNT(*) FROM papers")
    local_core = scalar(conn, "SELECT COUNT(*) FROM papers WHERE paper_role LIKE '%core%'")
    supplementary = scalar(conn, "SELECT COUNT(*) FROM papers WHERE paper_role LIKE '%supplement%'")
    external = scalar(conn, "SELECT COUNT(*) FROM external_literature")

    bic_types = rows(
        conn,
        "SELECT bic_type, COUNT(*) AS n FROM papers GROUP BY bic_type ORDER BY n DESC, bic_type LIMIT 12",
    )
    platforms = rows(
        conn,
        "SELECT platform, COUNT(*) AS n FROM papers GROUP BY platform ORDER BY n DESC, platform LIMIT 12",
    )
    priority = rows(
        conn,
        """
        SELECT paper_id, title, year, source, doi, bic_type, platform, priority
        FROM papers
        ORDER BY priority ASC, year ASC, title ASC
        LIMIT 15
        """,
    )
    high_overlap = rows(
        conn,
        """
        SELECT title, year, source, doi, arxiv, topic, overlap_level, relevance_notes
        FROM external_literature
        ORDER BY
            CASE overlap_level
                WHEN 'very high' THEN 0
                WHEN 'high' THEN 1
                WHEN 'medium-high' THEN 2
                ELSE 3
            END,
            year DESC
        """,
    )

    local_years = [r["year"] for r in rows(conn, "SELECT year FROM papers WHERE year IS NOT NULL")]
    year_summary = ""
    if local_years:
        counts = Counter(local_years)
        top_years = ", ".join(f"{year}: {counts[year]}" for year in sorted(counts))
        year_summary = f"Year coverage: {min(local_years)}-{max(local_years)}. Counts: {top_years}."

    report = f"""# BIC/qBIC Literature Database - Initial Build

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Executive Conclusion

The initial database contains **{total} local PDFs** and **{external} web-checked high-relevance external records**. It is already useful as a traceable literature skeleton, but numeric fields such as Q, resonance wavelength, linewidth, Fano q, geometry dimensions, and digitized spectra still need human/assisted curation from figures, tables, and supplements.

The novelty scan shows a clear risk: generic "ML predicts qBIC spectra/Q/Fano" has been done. The safer research position is **physics-informed Fourier-space learning of quasi-BIC spectra**, using 2D dielectric projections and FFT/k-space channels, with cross-topology generalization, Fano fitting, and interpretable Fourier attribution.

## Inventory

- Local PDF records: {total}
- Local core BIC records: {local_core}
- Supplementary/background records: {supplementary}
- External novelty-risk records: {external}
- {year_summary}

## Local BIC Type Distribution

{md_table(["BIC type", "Count"], [[r["bic_type"], r["n"]] for r in bic_types])}

## Platform Distribution

{md_table(["Platform", "Count"], [[r["platform"], r["n"]] for r in platforms])}

## Highest-Priority Local Papers

{md_table(
    ["ID", "Title", "Year", "Source", "DOI", "BIC type", "Platform", "Priority"],
    [[r["paper_id"], r["title"], r["year"], r["source"], r["doi"], r["bic_type"], r["platform"], r["priority"]] for r in priority],
)}

## External Novelty-Risk Map

{md_table(
    ["Title", "Year", "Source", "DOI/arXiv", "Topic", "Overlap", "Notes"],
    [[
        r["title"],
        r["year"],
        r["source"],
        (r["doi"] or "") + (("; arXiv:" + r["arxiv"]) if r["arxiv"] else ""),
        r["topic"],
        r["overlap_level"],
        r["relevance_notes"],
    ] for r in high_overlap],
)}

## Recommended Database Curation Steps

1. Mark duplicate or supplementary records. Known duplicates include the repeated Nature 2017 BIC laser PDF and manuscript/supplement pairs.
2. For the 10 highest-priority papers, extract one or two representative devices each: geometry family, material, period, thickness, asymmetry variable, BIC type, and experimental/simulation status.
3. Add numeric resonance rows only when each value has an `evidence_id` with page/figure/panel and evidence level.
4. Digitize spectra only after checking whether supplementary raw data exists. Store points in HDF5 and fitted parameters in SQLite.
5. Use the external novelty map as a standing veto list when writing research claims.

## Research Ideas To Carry Forward

### Idea 1 - Traceable qBIC Literature Database and Scaling Audit

Build a curated cross-paper database of qBIC structures, labels, evidence levels, and digitized spectra. Use it to audit reported scaling laws such as `Q ~ alpha^-2` under material loss, finite array size, substrate leakage, and fabrication uncertainty. This is lower risk than proposing another single geometry, because the contribution is traceable meta-analysis.

### Idea 2 - Fourier-Space qBIC Spectral Learning

Create a controlled numerical dataset where each sample stores `eps2d`, raw FFT, mean-subtracted FFT, scalar geometry/material parameters, spectra, and Fano labels. Compare real-space, k-space, scalar-only, and hybrid models. The scientific question is which Fourier components explain radiative coupling and Fano asymmetry, not merely whether a neural network predicts spectra.

### Idea 3 - Cross-Topology Generalization Benchmark

Train on several geometry families and hold out an entire topology. Evaluate whether k-space channels improve extrapolation of `lambda0`, `logQ`, `gamma`, and `Fano q`. This directly addresses the gap left by many same-topology inverse-design papers.

## Files Produced

- SQLite database: `{db_path}`
- CSV exports: `{PROJECT_DIR / "exports"}`
- HDF5 container: `{PROJECT_DIR / "data" / "bic_literature_arrays.h5"}`
- Schema: `{PROJECT_DIR / "schema.sql"}`
"""

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    conn.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--out", type=Path, default=DEFAULT_REPORT_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate(args.db, args.out)
    print(f"Wrote report: {args.out}")


if __name__ == "__main__":
    main()
