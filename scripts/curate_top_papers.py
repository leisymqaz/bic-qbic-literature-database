#!/usr/bin/env python
"""Add a small manually curated layer for the local BIC seed library."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PROJECT_DIR / "data" / "bic_literature.sqlite"


CURATION = {
    "Compact Surface Fano States Embedded in the Continuum of Waveguide Arrays.pdf": {
        "title": "Compact Surface Fano States Embedded in the Continuum of Waveguide Arrays",
        "year": 2013,
        "source": "Physical Review Letters",
        "doi": "10.1103/PhysRevLett.111.240403",
        "paper_role": "Fano compact-state experiment/theory",
        "bic_type": "Fano compact localized state",
        "platform": "waveguide array",
        "priority": 2,
    },
    "Dielectric microcavities Model systems for wave chaos.pdf": {
        "title": "Dielectric microcavities: Model systems for wave chaos and non-Hermitian physics",
        "year": 2015,
        "source": "Reviews of Modern Physics",
        "doi": "10.1103/RevModPhys.87.61",
        "paper_role": "background review",
        "bic_type": "non-Hermitian high-Q background",
        "platform": "dielectric microcavities",
        "priority": 4,
    },
    "Embedded Photonic Eigenvalues in 3D Nanostructures.pdf": {
        "title": "Embedded Photonic Eigenvalues in 3D Nanostructures",
        "year": 2014,
        "source": "Physical Review Letters",
        "doi": "10.1103/PhysRevLett.112.213903",
        "paper_role": "core embedded-eigenvalue BIC",
        "bic_type": "embedded photonic eigenvalue / finite photonic BIC",
        "platform": "three-dimensional nanostructure",
        "priority": 2,
    },
    "JOSA2003-PhCFanoCMT.pdf": {
        "title": "Temporal coupled-mode theory for Fano resonance in optical resonators",
        "year": 2003,
        "source": "Journal of the Optical Society of America A",
        "paper_role": "coupled-mode/Fano theory",
        "bic_type": "Fano/CMT theory background",
        "platform": "optical resonator / photonic crystal slab",
        "priority": 2,
    },
    "Light guiding above the light line in arrays of dielectric sphere.pdf": {
        "title": "Light guiding above the light line in arrays of dielectric spheres",
        "year": 2016,
        "source": "Optics Letters",
        "doi": "10.1364/OL.41.003888",
        "arxiv": "1603.02815",
        "paper_role": "core quasi-BIC guided mode",
        "bic_type": "quasi-BIC guided mode",
        "platform": "dielectric sphere array",
        "priority": 2,
    },
    "Light trapping above the light cone in a one-dimensional array of dielectric spheres.pdf": {
        "title": "Light trapping above the light cone in a one-dimensional array of dielectric spheres",
        "year": 2015,
        "source": "Physical Review A",
        "doi": "10.1103/PhysRevA.92.023816",
        "paper_role": "core BIC guided mode",
        "bic_type": "symmetry-protected and robust Bloch BIC",
        "platform": "one-dimensional dielectric sphere array",
        "priority": 2,
    },
    "Observation and differentiation of unique high-Q optical resonances.pdf": {
        "title": "Observation and differentiation of unique high-Q optical resonances near zero wave vector in macroscopic photonic crystal slabs",
        "year": 2012,
        "source": "Physical Review Letters",
        "doi": "10.1103/PhysRevLett.109.067401",
        "paper_role": "core high-Q guided resonance",
        "bic_type": "symmetry-protected Gamma-point quasi-BIC/Fano resonance",
        "platform": "macroscopic photonic crystal slab",
        "priority": 2,
    },
    "Observation of Localized States in Lieb Photonic Lattices.pdf": {
        "title": "Observation of Localized States in Lieb Photonic Lattices",
        "year": 2015,
        "source": "Physical Review Letters",
        "doi": "10.1103/PhysRevLett.114.245503",
        "paper_role": "flat-band/compact-state adjacent",
        "bic_type": "flat-band compact localized state in continuum",
        "platform": "Lieb photonic lattice",
        "priority": 3,
    },
    "Resonant transmission near nonrobust periodic slab modes.pdf": {
        "title": "Resonant transmission near nonrobust periodic slab modes",
        "year": 2005,
        "source": "Physical Review E",
        "doi": "10.1103/PhysRevE.71.026611",
        "paper_role": "periodic slab scattering theory",
        "bic_type": "nonrobust guided mode / BIC mathematical precursor",
        "platform": "periodic slab",
        "priority": 3,
    },
    "srep36066.pdf": {
        "title": "Normal incidence filters using symmetry-protected modes in dielectric subwavelength gratings",
        "year": 2016,
        "source": "Scientific Reports",
        "doi": "10.1038/srep36066",
        "paper_role": "quasi-BIC filtering application",
        "bic_type": "symmetry-protected quasi-BIC",
        "platform": "dielectric subwavelength grating",
        "priority": 2,
    },
    "Topological Subspace-Induced Bound State in the Continuum.pdf": {
        "title": "Topological Subspace-Induced Bound State in the Continuum",
        "year": 2017,
        "source": "Physical Review Letters",
        "doi": "10.1103/PhysRevLett.118.166803",
        "paper_role": "topological BIC theory/experiment",
        "bic_type": "topological subspace-induced BIC",
        "platform": "coupled one-dimensional chains / acoustic resonators",
        "priority": 2,
    },
    "光栅理论计算.pdf": {
        "title": "Normal-incidence filtering using symmetry-protected modes in dielectric subwavelength gratings",
        "year": 2015,
        "source": "Optics Letters",
        "doi": "10.1364/OL.40.002637",
        "paper_role": "quasi-BIC filtering application",
        "bic_type": "symmetry-protected quasi-BIC",
        "platform": "dielectric subwavelength grating",
        "priority": 3,
    },
    "TMM_Optical field calculations for lossy multiple-layer AlxGa1_xN_InxGa1_xN diodes.pdf": {
        "title": "Optical-field calculations for lossy multiple-layer AlxGa1-xN/InxGa1-xN laser diodes",
        "year": 1998,
        "source": "Journal of Applied Physics",
        "doi": "10.1063/1.368185",
        "paper_role": "transfer-matrix method background",
        "bic_type": "non-BIC optical multilayer method",
        "platform": "lossy multilayer laser diode",
        "priority": 5,
    },
    "Science2014-PT对称单模激光.pdf": {
        "title": "Single-mode laser by parity-time symmetry breaking",
        "year": 2014,
        "source": "Science",
        "doi": "10.1126/science.1258479",
        "paper_role": "non-Hermitian laser background",
        "bic_type": "non-BIC PT-symmetric laser",
        "platform": "microring resonator",
        "priority": 5,
    },
    "没看Light enhancement by quasi-bound states in.pdf": {
        "title": "Light enhancement by quasi-bound states in the continuum in dielectric arrays",
        "year": 2017,
        "source": "Optics Express",
        "doi": "10.1364/OE.25.014134",
        "paper_role": "core quasi-BIC enhancement",
        "bic_type": "quasi-BIC / finite-array light enhancement",
        "platform": "dielectric particle array",
        "priority": 2,
    },
}


def curate(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    for file_name, fields in CURATION.items():
        assignments = ", ".join(f"{key}=?" for key in fields)
        values = list(fields.values()) + [file_name]
        conn.execute(
            f"UPDATE papers SET {assignments}, review_status='seed_curated' WHERE file_name=?",
            values,
        )
        conn.execute(
            """
            UPDATE claims
            SET claim_text = (
                SELECT papers.bic_type || ' in ' || papers.platform
                FROM papers
                WHERE papers.paper_id = claims.paper_id
            ),
            claim_type='seed_curated_classification',
            structure_family=(SELECT platform FROM papers WHERE papers.paper_id = claims.paper_id),
            notes='Seed curation added from local filename/front-matter review; verify numeric claims before use.'
            WHERE paper_id = (SELECT paper_id FROM papers WHERE file_name=?)
            """,
            [file_name],
        )
        conn.execute(
            """
            UPDATE devices
            SET geometry_family=(SELECT platform FROM papers WHERE papers.paper_id = devices.paper_id),
                notes='Seed-curated placeholder device row for later parameter extraction.'
            WHERE paper_id=(SELECT paper_id FROM papers WHERE file_name=?)
            """,
            [file_name],
        )
    conn.commit()
    conn.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    curate(args.db)
    print(f"Applied seed curation to {args.db}")


if __name__ == "__main__":
    main()
