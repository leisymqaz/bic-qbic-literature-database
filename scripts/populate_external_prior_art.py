#!/usr/bin/env python
"""Populate externally verified prior-art records with source links."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PROJECT_DIR / "data" / "bic_literature_verified.sqlite"


PRIOR_ART = [
    {
        "external_id": "EXT-2022-LPR-RIDL",
        "title": "Strategical Deep Learning for Photonic Bound States in the Continuum",
        "year": 2022,
        "source": "Laser & Photonics Reviews",
        "doi": "10.1002/lpor.202100658",
        "arxiv": "2105.03001",
        "url": "https://doi.org/10.1002/lpor.202100658",
        "source_kind": "doi/publisher_record",
        "relevance_scope": "BIC/qBIC spectra and inverse design with resonance-informed deep learning",
        "overlap_risk": "very_high",
        "notes": "Blocks broad claims of first physics-informed or resonance-informed deep learning for photonic BIC spectra/inverse design.",
    },
    {
        "external_id": "EXT-2023-OL-RF-BIC",
        "title": "Infrared bound states in the continuum: random forest method",
        "year": 2023,
        "source": "Optics Letters",
        "doi": "10.1364/OL.494629",
        "arxiv": None,
        "url": "https://opg.optica.org/ol/abstract.cfm?URI=ol-48-17-4460",
        "source_kind": "publisher_record",
        "relevance_scope": "Random forest predicts BIC frequency from all-dielectric grating parameters.",
        "overlap_risk": "high",
        "notes": "Blocks broad claims of first ML prediction of BIC frequency/subband.",
    },
    {
        "external_id": "EXT-2023-NANOPH-ACCIDENTAL-BIC",
        "title": "Inverse design of all-dielectric metasurfaces with accidental bound states in the continuum",
        "year": 2023,
        "source": "Nanophotonics",
        "doi": "10.1515/nanoph-2023-0373",
        "arxiv": "2305.10020",
        "url": "https://doi.org/10.1515/nanoph-2023-0373",
        "source_kind": "doi/publisher_record",
        "relevance_scope": "Physics-inspired inverse design of accidental BIC metasurfaces.",
        "overlap_risk": "high",
        "notes": "Blocks broad claims of first all-dielectric BIC inverse design.",
    },
    {
        "external_id": "EXT-2024-ADVS-METAFORMER",
        "title": "Meta-Attention Deep Learning for Smart Development of Metasurface Sensors",
        "year": 2024,
        "source": "Advanced Science",
        "doi": "10.1002/advs.202405750",
        "arxiv": None,
        "url": "https://doi.org/10.1002/advs.202405750",
        "source_kind": "doi/publisher_record",
        "relevance_scope": "Explainable attention model for high-Q spectral metasurface sensors.",
        "overlap_risk": "high",
        "notes": "Blocks broad claims of first explainable/attention deep learning for high-Q metasurface spectra.",
    },
    {
        "external_id": "EXT-2025-SREP-FANO-RF",
        "title": "Machine learning method for predicting line-shapes of Fano resonances induced by bound states in the continuum",
        "year": 2025,
        "source": "Scientific Reports",
        "doi": "10.1038/s41598-025-16192-1",
        "arxiv": "2504.08409",
        "url": "https://www.nature.com/articles/s41598-025-16192-1",
        "source_kind": "publisher_record",
        "relevance_scope": "Random forest predicts BIC-induced Fano line-shape parameters from FEM-generated data.",
        "overlap_risk": "very_high",
        "notes": "Blocks broad claims of first ML prediction of BIC-induced Fano line shape or Fano parameters.",
    },
    {
        "external_id": "EXT-2025-OPTCOM-DUAL-FANO-DL",
        "title": "Inverse design of polarization-insensitive all-dielectric BIC metasurface with dual Fano-resonances by deep learning",
        "year": 2025,
        "source": "Optics Communications",
        "doi": "10.1016/j.optcom.2025.131964",
        "arxiv": None,
        "url": "https://doi.org/10.1016/j.optcom.2025.131964",
        "source_kind": "doi/publisher_record",
        "relevance_scope": "Deep-learning inverse design for all-dielectric BIC metasurface with dual Fano resonances.",
        "overlap_risk": "high",
        "notes": "Blocks broad claims of first deep-learning inverse design for complete qBIC/Fano spectra.",
    },
    {
        "external_id": "EXT-2026-PHOTONIX-FOURIER-SURFACES",
        "title": "Reality-infused deep learning for angle-resolved quasi-optical Fourier surfaces",
        "year": 2026,
        "source": "PhotoniX",
        "doi": "10.1186/s43074-026-00238-2",
        "arxiv": None,
        "url": "https://link.springer.com/article/10.1186/s43074-026-00238-2",
        "source_kind": "publisher_record",
        "relevance_scope": "Experiment-driven transformer learning for angle-resolved spectra of quasi-optical Fourier surfaces.",
        "overlap_risk": "high_adjacent",
        "notes": "Strong adjacent risk for Fourier/k-space, angle-resolved metasurface spectra, and deep learning claims.",
    },
    {
        "external_id": "EXT-2026-PRJ-SPECVIT",
        "title": "Transformer-Enabled Intelligent Design of High-Q Quasi-BIC Metasurface for Molecular Vibrational Fingerprinting",
        "year": 2026,
        "source": "Photonics Research",
        "doi": "10.1364/PRJ.578302",
        "arxiv": None,
        "url": "https://doi.org/10.1364/PRJ.578302",
        "source_kind": "doi/publisher_record",
        "relevance_scope": "Transformer spectral prediction and inverse design for high-Q quasi-BIC metasurfaces.",
        "overlap_risk": "very_high",
        "notes": "Blocks broad claims of first transformer/ViT high-Q qBIC metasurface spectral prediction or inverse design.",
    },
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    args = parser.parse_args()
    conn = sqlite3.connect(args.db)
    conn.execute("DELETE FROM external_verified_papers")
    for item in PRIOR_ART:
        conn.execute(
            """
            INSERT INTO external_verified_papers
            (external_id, title, year, source, doi, arxiv, url, source_kind, verification_status,
             checked_at, relevance_scope, overlap_risk, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'source_link_recorded_needs_periodic_recheck',
                    datetime('now'), ?, ?, ?)
            """,
            [
                item["external_id"],
                item["title"],
                item["year"],
                item["source"],
                item["doi"],
                item["arxiv"],
                item["url"],
                item["source_kind"],
                item["relevance_scope"],
                item["overlap_risk"],
                item["notes"],
            ],
        )
    conn.commit()
    conn.close()
    print(f"Inserted {len(PRIOR_ART)} external prior-art records")


if __name__ == "__main__":
    main()
