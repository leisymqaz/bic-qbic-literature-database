#!/usr/bin/env python
"""Generate the conservative verified-data project report."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PROJECT_DIR / "data" / "bic_literature_verified.sqlite"
DEFAULT_REPORT_PATH = PROJECT_DIR / "reports" / "verified_bic_research_report.md"


def table(headers: list[str], rows: list[list[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        safe = [str(x or "").replace("|", "\\|").replace("\n", " ") for x in row]
        lines.append("| " + " | ".join(safe) + " |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--out", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    counts = {
        "source_files": conn.execute("SELECT COUNT(*) FROM source_files").fetchone()[0],
        "papers": conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0],
        "manual_core": conn.execute("SELECT COUNT(*) FROM papers WHERE verification_status='manual_pdf_verified_core'").fetchone()[0],
        "doi_title_match": conn.execute("SELECT COUNT(*) FROM papers WHERE verification_status='doi_crossref_resolved_title_match'").fetchone()[0],
        "external": conn.execute("SELECT COUNT(*) FROM external_verified_papers").fetchone()[0],
        "devices": conn.execute("SELECT COUNT(*) FROM devices").fetchone()[0],
        "resonances": conn.execute("SELECT COUNT(*) FROM resonances").fetchone()[0],
        "physical_observations": conn.execute("SELECT COUNT(*) FROM physical_observations").fetchone()[0],
        "web_sources": conn.execute("SELECT COUNT(*) FROM web_sources").fetchone()[0],
    }
    core = conn.execute(
        """
        SELECT p.paper_id, sf.file_name, p.title, p.year, p.source, p.doi, p.arxiv, p.verification_status
        FROM papers p JOIN source_files sf USING(file_id)
        WHERE p.verification_status='manual_pdf_verified_core'
        ORDER BY p.year, p.title
        """
    ).fetchall()
    status_rows = conn.execute("SELECT verification_status, COUNT(*) n FROM papers GROUP BY verification_status ORDER BY n DESC").fetchall()
    external = conn.execute(
        """
        SELECT title, year, source, doi, arxiv, url, overlap_risk, notes
        FROM external_verified_papers
        ORDER BY CASE overlap_risk WHEN 'very_high' THEN 0 WHEN 'high' THEN 1 ELSE 2 END, year
        """
    ).fetchall()
    obs_summary = conn.execute(
        """
        SELECT source_kind, observation_type, COUNT(*) n
        FROM physical_observations
        GROUP BY source_kind, observation_type
        ORDER BY source_kind, n DESC
        """
    ).fetchall()
    web_obs = conn.execute(
        """
        SELECT quantity_name, value_text, material, quote, source_url, notes
        FROM physical_observations
        WHERE source_kind='web_article_text'
        ORDER BY source_url, observation_id
        """
    ).fetchall()
    candidates = conn.execute(
        """
        SELECT candidate_field, candidate_value, COUNT(*) n
        FROM candidate_classifications
        GROUP BY candidate_field, candidate_value
        ORDER BY candidate_field, n DESC
        """
    ).fetchall()

    report = f"""# Verified BIC/qBIC Research Report

## Boundary

This report separates real source-backed data from candidate interpretation. The database currently contains bibliographic/source-file facts and evidence text. It intentionally contains **no verified device rows and no verified resonance/Q/Fano numeric rows** yet, because those require page/figure/table-level curation or digitized spectra with uncertainty.

## Database State

- Source PDFs indexed: {counts['source_files']}
- Paper records: {counts['papers']}
- Core papers promoted after local PDF quote/id checks: {counts['manual_core']}
- DOI/Crossref title-match records not manually promoted: {counts['doi_title_match']}
- External prior-art source-link records: {counts['external']}
- Web source records with physical observations: {counts['web_sources']}
- Source-quoted physical observation rows: {counts['physical_observations']}
- Verified devices: {counts['devices']}
- Verified resonances: {counts['resonances']}

## Paper Verification Status

{table(['Status', 'Count'], [[r['verification_status'], r['n']] for r in status_rows])}

## Core Bibliography Verified From Local PDFs

{table(['ID', 'File', 'Title', 'Year', 'Source', 'DOI', 'arXiv', 'Status'], [[r['paper_id'], r['file_name'], r['title'], r['year'], r['source'], r['doi'], r['arxiv'], r['verification_status']] for r in core])}

## Candidate Classifications Are Not Facts

The following are review queues only. They should guide manual reading, not be cited as database facts.

{table(['Candidate field', 'Candidate value', 'Count'], [[r['candidate_field'], r['candidate_value'], r['n']] for r in candidates[:30]])}

## Verified External Prior-Art Risk

{table(['Title', 'Year', 'Source', 'DOI/arXiv', 'Risk', 'Source link', 'Blocked claim'], [[r['title'], r['year'], r['source'], (r['doi'] or '') + (('; arXiv:' + r['arxiv']) if r['arxiv'] else ''), r['overlap_risk'], r['url'], r['notes']] for r in external])}

## Physical Observation Review Queue

These rows are the central database object for the user's requested physics data: structure parameters, materials, Q, wavelength/frequency, Fano, linewidth, spectra, k-space, band structure, and polarization/topology. Rows are source-quoted and reviewable, but most are not yet human-verified.

{table(['Source kind', 'Observation type', 'Count'], [[r['source_kind'], r['observation_type'], r['n']] for r in obs_summary])}

## Web-Source Physical Observations Added Beyond Local PDFs

{table(['Quantity', 'Value', 'Material/structure', 'Quote', 'Source URL', 'Note'], [[r['quantity_name'], r['value_text'], r['material'], r['quote'], r['source_url'], r['notes']] for r in web_obs])}

## Novelty Position After Verification

Unsafe claims:

- First use of ML/DL to predict BIC/qBIC spectra, Q, or Fano line shapes.
- First inverse design of all-dielectric BIC/qBIC metasurfaces.
- First transformer/attention model for high-Q qBIC metasurfaces.
- First Fourier/k-space or angle-resolved deep-learning treatment of metasurface spectra.

Lower-risk research direction:

> Build a traceable qBIC literature and simulation benchmark centered on 2D dielectric-projection FFT/k-space representations, with Fano/TCMT labels, real-space vs k-space ablations, hard topology/mechanism splits, and Fourier-mode perturbation tests that verify attribution against full-wave simulations.

## Few Research Ideas Worth Keeping

1. **Fourier harmonics to TCMT radiative-coupling causality.** Use structure-resolved `epsilon(x,y)` and FFT channels to perturb selected Fourier shells/symmetry channels, then rerun full-wave simulation and fit TCMT/Fano parameters. The question is which dielectric Fourier harmonics control `gamma_rad`, Fano zero/pole position, and far-field polarization vortex, not whether a model predicts spectra.

2. **Topology-charge-aware finite-size/loss/Q-scaling phase diagram.** Curate and simulate `1/Q = 1/Q_rad(alpha,N,charge) + 1/Q_abs + 1/Q_edge + 1/Q_disorder`. The physics target is where `Q ~ alpha^-2` fails because of finite array size, absorption, substrate leakage, roughness, and topological charge merging/annihilation.

3. **Fourier-disorder engineering of roughness-induced qBIC leakage.** Treat fabrication disorder as a measured boundary Fourier spectrum instead of a scalar RMS error. Ask which disorder bands destroy or preserve Q, Fano asymmetry, and polarization-vortex topology.

4. **Reconfigurable channel-selective Janus qBIC.** Use refractive-index detuning, phase-change layers, or liquid crystal tuning to split upward/downward radiation-channel topology and Fano response without relying only on geometric asymmetry. This must be framed as reconfigurable channel-selective qBIC control, not as first Janus BIC.

## Immediate Next Work

1. For each manually verified core paper, create one curated `devices` row only after reading the exact structure description and recording page/figure/table evidence.
2. Add `resonances` only from direct tables/text or digitized spectra with calibration, uncertainty, and fit formula.
3. Search for supplementary raw data before digitizing figures.
4. Keep synthetic/proxy experiments in `sandbox_non_database`; do not mix them with real literature data.
"""

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    conn.close()
    print(f"Wrote report: {args.out}")


if __name__ == "__main__":
    main()
