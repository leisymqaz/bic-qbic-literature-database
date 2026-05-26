#!/usr/bin/env python
"""Insert source-linked web physical observations into the verified database."""

from __future__ import annotations

import argparse
import hashlib
import sqlite3
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PROJECT_DIR / "data" / "bic_literature_verified.sqlite"


WEB_PAPERS = [
    {
        "id": "WEB-NC-2023-ULTRAHIGH-Q-GMR",
        "title": "Ultrahigh-Q guided mode resonances in an all-dielectric metasurface",
        "year": 2023,
        "source": "Nature Communications",
        "doi": "10.1038/s41467-023-39227-5",
        "url": "https://www.nature.com/articles/s41467-023-39227-5",
        "observations": [
            ("resonance", "q_factor", "Q factor", "2.39 × 10^5", 2.39e5, None, None, None, None, None, "The experimental results show that the Q-factor was as high as 2.39 × 10^{5}, comparable to the maximum Q-factor of topological BICs.", "Nature Communications article text lines 95-98"),
            ("structure", "material", "material/platform", "low-index photoresist on SOI waveguide", None, None, None, None, None, "photoresist; SOI", "Instead of patterning the high-index layer to form a Mie resonator in a unit cell, we introduced an ultrathin photoresist layer as a perturbation layer on top of a multilayer-waveguide system.", "Nature Communications article text lines 95-98"),
            ("resonance", "scaling_law", "Q-alpha scaling", "Q ∝ α−2", None, None, None, None, None, None, "High Q-factors of GMRs can be easily realized as they are inversely proportional to the perturbation parameter squared (Q ∝ α−2).", "Nature Communications article text line 96"),
        ],
    },
    {
        "id": "WEB-NC-2024-MILLION-Q",
        "title": "Million-Q free space meta-optical resonator at near-visible wavelengths",
        "year": 2024,
        "source": "Nature Communications",
        "doi": "10.1038/s41467-024-54775-0",
        "url": "https://www.nature.com/articles/s41467-024-54775-0",
        "observations": [
            ("structure", "geometry_parameter", "layer stack and period", "58 nm PMMA / 100 nm SiN / 1470 nm SiO2; P=500 nm; L=50 nm", None, "nm", 500, None, None, "PMMA; SiN; SiO2; Si", "Schematic showing the unit cell ... 58 nm-thick patterned PMMA layer, a 100-nm-thick SiN layer, and a 1470 nm-thick SiO2 layer on a Si substrate. The patterning is defined by the period P and defect hole size L.", "Nature Communications article text lines 111-112"),
            ("resonance", "q_factor", "Q factor", "1.10 million", 1.10e6, None, None, None, None, None, "The Fano fitting (pink curve) reveals a Q factor of 1.10 million.", "Nature Communications article text line 174"),
            ("kspace", "momentum_space_spectroscopy", "momentum-space resolved spectroscopy", "0.42 pm/pixel wavelength resolution; 0.028 deg/pixel angle resolution", None, None, None, None, None, None, "The Γ-point data are extracted from extra-fine laser-scanning momentum-space-resolved reflectance spectroscopy with a wavelength resolution of ~0.42 pm/pixel and an angle resolution of ~0.028 ̊ /pixel.", "Nature Communications article text line 174"),
        ],
    },
    {
        "id": "WEB-NC-2024-AIR-MEMBRANE",
        "title": "Trapping light in air with membrane metasurfaces for vibrational strong coupling",
        "year": 2024,
        "source": "Nature Communications",
        "doi": "10.1038/s41467-024-54284-0",
        "url": "https://www.nature.com/articles/s41467-024-54284-0",
        "observations": [
            ("resonance", "q_factor", "qBIC TE Q", "722", 722, None, None, None, None, None, "We measured a maximum Q-factor of 722 for the qBIC TE mode (Fig. 3d) and 463 for the qBIC TM mode.", "Nature Communications article text line 146"),
            ("resonance", "q_factor", "qBIC TM Q", "463", 463, None, None, None, None, None, "We measured a maximum Q-factor of 722 for the qBIC TE mode (Fig. 3d) and 463 for the qBIC TM mode.", "Nature Communications article text line 146"),
            ("resonance", "scaling_law", "Q-alpha scaling", "inverse quadratic relationship", None, None, None, None, None, None, "We also plotted the FTIR-measured and simulation-estimated Q-factor values of the qBIC TE mode and observed an inverse quadratic relationship between Q and the asymmetry parameter α.", "Nature Communications article text line 147"),
            ("resonance", "linewidth", "FWHM", "~13 cm−1 average", 13, "cm−1", None, None, None, None, "The average FWHM of the fabricated qBIC TM resonances shown in Fig. 4b is ~ 13 cm−1, i.e., the average loss is 6.5 cm−1.", "Nature Communications article text line 151"),
        ],
    },
    {
        "id": "WEB-NC-2025-PLDOS-BIC",
        "title": "Near-field probing of the local density of optical states enhanced by bound states in the continuum in nonlocal metasurfaces",
        "year": 2025,
        "source": "Nature Communications",
        "doi": "10.1038/s41467-025-66653-4",
        "url": "https://www.nature.com/articles/s41467-025-66653-4",
        "observations": [
            ("structure", "geometry_parameter", "rod separation", "d = 80 μm", 80, "μm", None, None, None, None, "The inset shows an optical microscope image of a unit cell in the fabricated metasurface, where the separation between the rods is d = 80 μm.", "Nature Communications article text line 108"),
            ("resonance", "frequency", "broad even mode frequency", "0.495 THz", 0.495, "THz", None, 0.495, None, None, "The broad resonance in the transmission spectrum at 0.495 THz corresponds to the even mode in the array.", "Nature Communications article text line 113"),
            ("resonance", "frequency", "off-normal quasi-BIC frequency", "0.365 THz", 0.365, "THz", None, 0.365, None, None, "A narrow feature appears in T(ω, θ) around 0.365 THz for off-normal incidence (θ = 40°).", "Nature Communications article text line 113"),
            ("resonance", "frequency", "BIC frequency / PLDOS", "0.395 THz", 0.395, "THz", None, 0.395, None, None, "The PLDOS enhancement reaches a maximum at the BIC frequency of 0.395 THz for both polarizations and is confined within a height of 20μm from the surface.", "Nature Communications article text line 195"),
            ("resonance", "q_factor_definition", "Q definition", "Q=f0/Δf", None, None, None, None, None, None, "The symbols represent the extracted quality factor (Q-factor) of the quasi-BIC mode, given by Q = f0/Δf ... retrieved from Fano fitting.", "Nature Communications article text line 110"),
        ],
    },
]


def short_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:16]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    args = parser.parse_args()
    conn = sqlite3.connect(args.db)
    conn.execute("DELETE FROM physical_observations WHERE source_kind='web_article_text'")
    conn.execute("DELETE FROM web_sources")
    inserted = 0
    for paper in WEB_PAPERS:
        conn.execute(
            """
            INSERT OR REPLACE INTO web_sources
            (web_source_id, title, url, doi, year, publisher, source_kind, checked_at, accessible_text_excerpt, notes)
            VALUES (?, ?, ?, ?, ?, ?, 'publisher_article_html', datetime('now'), ?, ?)
            """,
            [
                paper["id"],
                paper["title"],
                paper["url"],
                paper["doi"],
                paper["year"],
                paper["source"],
                paper["observations"][0][10],
                "Source text retrieved from publisher article page and inserted as source-linked observations.",
            ],
        )
        ext_id = f"EXT-WEB-{paper['id']}"
        conn.execute(
            """
            INSERT OR REPLACE INTO external_verified_papers
            (external_id, title, year, source, doi, url, source_kind, verification_status, checked_at,
             relevance_scope, overlap_risk, notes)
            VALUES (?, ?, ?, ?, ?, ?, 'publisher_article_html', 'source_link_recorded_with_physical_observations',
                    datetime('now'), ?, ?, ?)
            """,
            [
                ext_id,
                paper["title"],
                paper["year"],
                paper["source"],
                paper["doi"],
                paper["url"],
                "Physical qBIC/BIC result source with quoted observation rows.",
                "result_database_source",
                "Web source added beyond local 50 PDFs.",
            ],
        )
        for idx, obs in enumerate(paper["observations"], start=1):
            group, obs_type, quantity, value_text, value_num, unit, wavelength, freq, q, material, quote, note = obs
            obs_id = f"OBS-{paper['id']}-{idx:02d}"
            conn.execute(
                """
                INSERT OR REPLACE INTO physical_observations
                (observation_id, external_id, observation_group, observation_type, quantity_name,
                 value_text, value_numeric, unit, material, wavelength_nm, frequency_thz, q_factor,
                 source_kind, source_url, quote, extraction_method, verification_status, curation_status,
                 confidence, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'web_article_text', ?, ?, 'manual_web_source_quote',
                        'source_quote_recorded_needs_secondary_check', 'review_queue', 0.82, ?)
                """,
                [
                    obs_id,
                    ext_id,
                    group,
                    obs_type,
                    quantity,
                    value_text,
                    value_num,
                    unit,
                    material,
                    wavelength,
                    freq,
                    q if q is not None else (value_num if obs_type == "q_factor" else None),
                    paper["url"],
                    quote,
                    note,
                ],
            )
            inserted += 1
    conn.commit()
    conn.close()
    print(f"Inserted {inserted} web physical observations")


if __name__ == "__main__":
    main()
