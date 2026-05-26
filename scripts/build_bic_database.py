#!/usr/bin/env python
"""Build an initial traceable BIC/qBIC literature database from local PDFs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import h5py
import numpy as np

try:
    import fitz  # PyMuPDF
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyMuPDF is required: install package 'pymupdf'.") from exc


PROJECT_DIR = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_DIR / "schema.sql"
DEFAULT_SOURCE_DIR = Path("pdfs")
DEFAULT_DB_PATH = PROJECT_DIR / "data" / "bic_literature.sqlite"
DEFAULT_H5_PATH = PROJECT_DIR / "data" / "bic_literature_arrays.h5"
DEFAULT_EXPORT_DIR = PROJECT_DIR / "exports"


CURATED_HINTS: list[dict[str, Any]] = [
    {
        "contains": "s41377-019-0227-x",
        "title": "Cooperative interactions between nano-antennas in a high-Q cavity",
        "year": 2019,
        "source": "Light: Science & Applications",
        "doi": "10.1038/s41377-019-0227-x",
        "paper_role": "high-Q BIC-adjacent",
        "bic_type": "BIC-adjacent high-Q cavity",
        "platform": "dielectric microdisk and nano-antennas",
        "priority": 4,
    },
    {
        "contains": "1909.12618",
        "title": "Generating optical vortex beams by momentum-space polarization vortices centred at bound states in the continuum",
        "year": 2019,
        "arxiv": "1909.12618",
        "paper_role": "core BIC application",
        "bic_type": "topological BIC",
        "platform": "photonic crystal slab",
        "mechanism": "momentum-space polarization vortex",
        "priority": 1,
    },
    {
        "contains": "acsphotonics.6b00026",
        "title": "Substrate-Independent Light Confinement in Bioinspired All-Dielectric Surface Resonators",
        "year": 2016,
        "source": "ACS Photonics",
        "doi": "10.1021/acsphotonics.6b00026",
        "paper_role": "guided-resonance adjacent",
        "bic_type": "quasi-BIC adjacent guided resonance",
        "platform": "all-dielectric surface resonator",
        "priority": 4,
    },
    {
        "contains": "advanced photonics2021",
        "title": "Pushing the limit of high-Q mode of a single dielectric nanocavity",
        "year": 2021,
        "source": "Advanced Photonics",
        "doi": "10.1117/1.AP.3.1.016004",
        "paper_role": "core quasi-BIC",
        "bic_type": "quasi-BIC",
        "platform": "single dielectric nanocavity",
        "mechanism": "avoided crossing / interfering resonances",
        "priority": 2,
    },
    {
        "contains": "analytical perspective of interfering resonances",
        "title": "Analytical Perspective of Interfering Resonances in High-Index-Contrast Periodic Photonic Structures",
        "year": 2016,
        "source": "IEEE Journal of Quantum Electronics",
        "doi": "10.1109/JQE.2016.2568763",
        "paper_role": "theory",
        "bic_type": "Friedrich-Wintgen / interfering-resonance BIC",
        "platform": "periodic photonic structures",
        "priority": 2,
    },
    {
        "contains": "experimental observation of optical bound states",
        "title": "Experimental Observation of Optical Bound States in the Continuum",
        "year": 2011,
        "source": "Physical Review Letters",
        "doi": "10.1103/PhysRevLett.107.183901",
        "paper_role": "core experiment",
        "bic_type": "symmetry-protected BIC",
        "platform": "optical waveguide array",
        "priority": 1,
    },
    {
        "contains": "nature photon2017-anisotropy",
        "title": "Anisotropy-induced photonic bound states in the continuum",
        "year": 2017,
        "source": "Nature Photonics",
        "doi": "10.1038/NPHOTON.2017.31",
        "paper_role": "core BIC mechanism",
        "bic_type": "anisotropy-induced BIC",
        "platform": "anisotropic waveguide / slab",
        "priority": 1,
    },
    {
        "contains": "nature2017-lasing action from photonic bound states",
        "title": "Lasing action from photonic bound states in continuum",
        "year": 2017,
        "source": "Nature",
        "doi": "10.1038/nature20799",
        "paper_role": "core BIC laser",
        "bic_type": "BIC laser",
        "platform": "cylindrical nanoresonator array",
        "priority": 1,
    },
    {
        "contains": "na-nano2018",
        "title": "Directional lasing in resonant semiconductor nanoantenna arrays",
        "year": 2018,
        "source": "Nature Nanotechnology",
        "doi": "10.1038/s41565-018-0245-5",
        "paper_role": "core BIC laser",
        "bic_type": "quasi-BIC laser",
        "platform": "active dielectric nanoantenna array",
        "priority": 1,
    },
    {
        "contains": "nc2022",
        "title": "Symmetry-guaranteed pairs of bound states in the continuum in metasurfaces",
        "year": 2022,
        "source": "Nature Communications",
        "doi": "10.1038/s41467-022-35246-w",
        "paper_role": "core metasurface BIC",
        "bic_type": "degenerate symmetry-protected BIC pair",
        "platform": "C6 silicon metasurface",
        "priority": 1,
    },
    {
        "contains": "s41467-023-41068-1",
        "title": "Twisted moire photonic crystal enabled optical vortex generation through bound states in the continuum",
        "year": 2023,
        "source": "Nature Communications",
        "doi": "10.1038/s41467-023-41068-1",
        "paper_role": "core topological BIC application",
        "bic_type": "topological BIC",
        "platform": "twisted bilayer photonic crystal",
        "mechanism": "moire and momentum-space vortex",
        "priority": 1,
    },
    {
        "contains": "physrevlett.113.037401",
        "title": "Analytical Perspective for Bound States in the Continuum in Photonic Crystal Slabs",
        "year": 2014,
        "source": "Physical Review Letters",
        "doi": "10.1103/PhysRevLett.113.037401",
        "paper_role": "core theory",
        "bic_type": "symmetry-protected and accidental BIC",
        "platform": "photonic crystal slab",
        "priority": 1,
    },
    {
        "contains": "prl2014",
        "title": "Topological Nature of Optical Bound States in the Continuum",
        "year": 2014,
        "source": "Physical Review Letters",
        "doi": "10.1103/PhysRevLett.113.257401",
        "paper_role": "core topology theory",
        "bic_type": "topological BIC",
        "platform": "photonic crystal slab",
        "mechanism": "polarization vortex and topological charge",
        "priority": 1,
    },
    {
        "contains": "srep-formation mechanism",
        "title": "Formation mechanism of guided resonances and bound states in the continuum in photonic crystal slabs",
        "year": 2016,
        "source": "Scientific Reports",
        "doi": "10.1038/srep31908",
        "paper_role": "core mechanism",
        "bic_type": "symmetry-protected and accidental BIC",
        "platform": "one-dimensional photonic crystal slab",
        "priority": 1,
    },
    {
        "contains": "quasi bound states in the continuum with few unit",
        "title": "Quasi-bound states in the continuum with few unit cells",
        "year": 2017,
        "arxiv": "1705.09842",
        "paper_role": "finite-size quasi-BIC",
        "bic_type": "finite-size quasi-BIC",
        "platform": "few-cell photonic crystal slab microcavity",
        "priority": 2,
    },
    {
        "contains": "nonradiating photonics",
        "title": "Nonradiating photonics with resonant dielectric nanostructures",
        "year": 2019,
        "source": "Nanophotonics",
        "doi": "10.1515/nanoph-2019-0024",
        "paper_role": "review",
        "bic_type": "review of BIC/anapole/nonradiating states",
        "platform": "resonant dielectric nanostructures",
        "priority": 2,
    },
]


EXTERNAL_SEEDS: list[dict[str, Any]] = [
    {
        "external_id": "EXT-ML-2022-RIDL",
        "title": "Strategical Deep Learning for Photonic Bound States in the Continuum",
        "year": 2022,
        "source": "Laser & Photonics Reviews",
        "doi": "10.1002/lpor.202100658",
        "arxiv": "2105.03001",
        "url": "https://doi.org/10.1002/lpor.202100658",
        "topic": "ML qBIC spectra",
        "overlap_level": "high",
        "relevance_notes": "Physics-informed spectral decomposition predicts high-Q BIC spectra and band structures.",
    },
    {
        "external_id": "EXT-ML-2023-RF-BIC",
        "title": "Infrared bound states in the continuum: random forest method",
        "year": 2023,
        "source": "Optics Letters",
        "doi": "10.1364/OL.494629",
        "url": "https://doi.org/10.1364/OL.494629",
        "topic": "ML BIC frequency",
        "overlap_level": "high",
        "relevance_notes": "Random forest predicts BIC frequencies from grating parameters.",
    },
    {
        "external_id": "EXT-ML-2023-ACCIDENTAL-BIC",
        "title": "Inverse design of all-dielectric metasurfaces with accidental bound states in the continuum",
        "year": 2023,
        "source": "Nanophotonics",
        "doi": "10.1515/nanoph-2023-0373",
        "arxiv": "2305.10020",
        "url": "https://doi.org/10.1515/nanoph-2023-0373",
        "topic": "ML inverse design BIC",
        "overlap_level": "medium-high",
        "relevance_notes": "Inverse design for accidental BICs; not centered on FFT geometry channels.",
    },
    {
        "external_id": "EXT-ML-2024-METAFORMER",
        "title": "Meta-Attention Deep Learning for Smart Development of Metasurface Sensors",
        "year": 2024,
        "source": "Advanced Science",
        "doi": "10.1002/advs.202405750",
        "url": "https://doi.org/10.1002/advs.202405750",
        "topic": "Transformer qBIC metasensors",
        "overlap_level": "high",
        "relevance_notes": "Transformer-style model for qBIC metasurface sensors and spectra.",
    },
    {
        "external_id": "EXT-ML-2025-FANO-RF",
        "title": "Machine learning method for predicting line-shapes of Fano resonances induced by bound states in the continuum",
        "year": 2025,
        "source": "Scientific Reports",
        "doi": "10.1038/s41598-025-16192-1",
        "arxiv": "2504.08409",
        "url": "https://doi.org/10.1038/s41598-025-16192-1",
        "topic": "ML Fano parameters",
        "overlap_level": "very high",
        "relevance_notes": "Closest known prior for Fano line-shape parameter prediction.",
    },
    {
        "external_id": "EXT-ML-2026-SPECVIT",
        "title": "Transformer-Enabled Intelligent Design of High-Q Quasi-BIC Metasurface for Molecular Vibrational Fingerprinting",
        "year": 2026,
        "source": "Photonics Research",
        "doi": "10.1364/PRJ.578302",
        "url": "https://doi.org/10.1364/PRJ.578302",
        "topic": "Transformer qBIC inverse design",
        "overlap_level": "high",
        "relevance_notes": "SpecViT/MetaViT for high-Q qBIC molecular sensing.",
    },
    {
        "external_id": "EXT-KSPACE-2014-TOPO-BIC",
        "title": "Topological Nature of Optical Bound States in the Continuum",
        "year": 2014,
        "source": "Physical Review Letters",
        "doi": "10.1103/PhysRevLett.113.257401",
        "url": "https://doi.org/10.1103/PhysRevLett.113.257401",
        "topic": "momentum-space topology",
        "overlap_level": "medium",
        "relevance_notes": "BICs as far-field polarization vortices; essential k-space theory baseline.",
    },
    {
        "external_id": "EXT-KSPACE-2025-POST-PCSEL",
        "title": "Photonic swin transformer for photonic crystal surface-emitting laser prediction",
        "year": 2025,
        "source": "PCSEL / transformer literature",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12592633/",
        "topic": "Fourier geometry representation",
        "overlap_level": "medium-high",
        "relevance_notes": "Uses 2D Fourier transform of dielectric constant distribution; nearby method but not qBIC spectra.",
    },
]


KEYWORDS = [
    "bound state in the continuum",
    "bound states in the continuum",
    "bic",
    "quasi-bic",
    "fano",
    "topological",
    "polarization vortex",
    "photonic crystal slab",
    "metasurface",
    "quality factor",
    "fano resonance",
    "lasing",
    "chiral",
    "fourier",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf(path: Path, max_pages: int) -> dict[str, Any]:
    result: dict[str, Any] = {
        "page_count": None,
        "metadata": {},
        "text": "",
        "error": None,
        "pages_read": 0,
    }
    try:
        doc = fitz.open(path)
        result["page_count"] = doc.page_count
        result["metadata"] = doc.metadata or {}
        pages = min(max_pages, doc.page_count)
        chunks = []
        for page_index in range(pages):
            page = doc.load_page(page_index)
            chunks.append(f"\n--- page {page_index + 1} ---\n{page.get_text('text')}")
        result["text"] = clean_text("\n".join(chunks))
        result["pages_read"] = pages
        doc.close()
    except Exception as exc:  # pragma: no cover
        result["error"] = repr(exc)
    return result


def extract_doi(text: str) -> str | None:
    match = re.search(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", text, re.IGNORECASE)
    if not match:
        return None
    doi = match.group(0).rstrip(".,;:)\\]")
    return doi


def extract_arxiv(text: str) -> str | None:
    match = re.search(r"(?:arXiv:?\s*)?(\d{4}\.\d{4,5})(?:v\d+)?", text, re.IGNORECASE)
    return match.group(1) if match else None


def extract_year(text: str, metadata: dict[str, Any]) -> int | None:
    date_text = " ".join(str(metadata.get(k, "")) for k in ("creationDate", "modDate"))
    for source in (date_text, text[:6000]):
        years = [int(y) for y in re.findall(r"\b(19[7-9]\d|20[0-2]\d)\b", source)]
        years = [y for y in years if 1970 <= y <= 2026]
        if years:
            return Counter(years).most_common(1)[0][0]
    return None


def filename_title(path: Path) -> str:
    stem = path.stem
    stem = re.sub(r"[_@]+", " ", stem)
    stem = re.sub(r"\b(?:pdf|supplementary|supplement|SM)\b", " ", stem, flags=re.IGNORECASE)
    stem = re.sub(r"\s+", " ", stem).strip()
    return stem


def metadata_title(metadata: dict[str, Any]) -> str | None:
    title = clean_text(str(metadata.get("title") or ""))
    if len(title) < 8:
        return None
    bad = ("microsoft word", "untitled", "elsevier", "paper", ".doc")
    if any(token in title.lower() for token in bad):
        return None
    return title


def first_page_title(text: str) -> str | None:
    lines = [clean_text(line) for line in text.splitlines()]
    lines = [line for line in lines if 12 <= len(line) <= 180]
    skip = (
        "--- page",
        "abstract",
        "introduction",
        "copyright",
        "downloaded",
        "arxiv",
        "doi",
        "www.",
        "microsoft",
        "licensed",
        "all rights reserved",
    )
    candidates = []
    for line in lines[:60]:
        lower = line.lower()
        if any(s in lower for s in skip):
            continue
        if re.fullmatch(r"[\d\s.]+", line):
            continue
        if len(line.split()) < 3:
            continue
        candidates.append(line)
    if not candidates:
        return None
    return candidates[0]


def abstract_candidate(text: str) -> str | None:
    match = re.search(r"\bAbstract\b[:\s]*(.{200,1800}?)(?:\n\s*(?:Introduction|1\.|Keywords)\b)", text, re.IGNORECASE | re.DOTALL)
    if match:
        return clean_text(match.group(1))[:1800]
    return None


def apply_curated_hint(path: Path) -> dict[str, Any]:
    lower = path.name.lower()
    for hint in CURATED_HINTS:
        token = hint["contains"].lower()
        if token in lower:
            return {k: v for k, v in hint.items() if k != "contains"}
    return {}


def classify(text: str, file_name: str) -> dict[str, Any]:
    name_head = f"{file_name}\n{text[:2500]}".lower()
    blob = f"{file_name}\n{text[:12000]}".lower()

    if any(t in blob for t in ("supplementary", "supporting information", "supplemental", "science sm")):
        paper_role = "supplementary"
    elif any(t in blob for t in ("review", "revmodphys", "spectroscopy and biosensing")):
        paper_role = "review"
    elif any(t in blob for t in ("fourier transform", "transfer matrix method", "temporal coupled-mode theory", "coupled-mode theory")):
        paper_role = "method/theory background"
    elif "bound state" in blob or "bound states" in blob or "bic" in blob:
        paper_role = "core BIC literature"
    else:
        paper_role = "adjacent/background"

    if "chiral" in name_head:
        bic_type = "chiral quasi-BIC"
    elif "lasing" in name_head or "laser" in name_head:
        bic_type = "BIC laser / quasi-BIC laser"
    elif "topological" in name_head or "polarization vortex" in name_head or "vortex" in name_head:
        bic_type = "topological / polarization-vortex BIC"
    elif "friedrich" in name_head or "accidental" in name_head or "interfering resonances" in name_head:
        bic_type = "accidental / Friedrich-Wintgen BIC"
    elif "symmetry-protected" in name_head or "symmetry protected" in name_head or "symmetry-guaranteed" in name_head:
        bic_type = "symmetry-protected BIC"
    elif "quasi" in name_head or "fano" in name_head:
        bic_type = "quasi-BIC / Fano resonance"
    elif "bound state" in blob or "bic" in blob:
        bic_type = "BIC general"
    else:
        bic_type = "non-BIC or adjacent"

    platform_rules = [
        ("photonic crystal slab", "photonic crystal slab"),
        ("phc slab", "photonic crystal slab"),
        ("metasurface", "metasurface"),
        ("grating", "diffraction/subwavelength grating"),
        ("waveguide array", "waveguide array"),
        ("nanoantenna", "dielectric nanoantenna array"),
        ("nanoparticle", "dielectric nanoparticle array"),
        ("nanosphere", "dielectric sphere array"),
        ("dielectric rods", "dielectric rod array"),
        ("microcavit", "dielectric microcavity"),
        ("ring", "ring / resonator"),
    ]
    platform = next((value for key, value in platform_rules if key in blob), "unknown / needs curation")

    mechanism_terms = []
    for key, value in [
        ("symmetry", "symmetry protection/breaking"),
        ("accidental", "accidental destructive interference"),
        ("friedrich", "Friedrich-Wintgen interference"),
        ("topological", "topological charge"),
        ("polarization vortex", "momentum-space polarization vortex"),
        ("anisotropy", "anisotropy induced"),
        ("finite", "finite-size leakage"),
        ("fano", "Fano interference"),
    ]:
        if key in blob:
            mechanism_terms.append(value)
    mechanism = "; ".join(dict.fromkeys(mechanism_terms)) or None

    if "experiment" in blob or "fabricat" in blob or "measured" in blob or "observation" in blob:
        experiment_or_theory = "experimental and/or measured"
    elif "simulation" in blob or "numerical" in blob or "fdtd" in blob or "fem" in blob:
        experiment_or_theory = "simulation/theory"
    else:
        experiment_or_theory = "unknown"

    keyword_hits = {kw: blob.count(kw) for kw in KEYWORDS if blob.count(kw)}
    return {
        "paper_role": paper_role,
        "bic_type": bic_type,
        "platform": platform,
        "mechanism": mechanism,
        "experiment_or_theory": experiment_or_theory,
        "keyword_hits": keyword_hits,
    }


def guess_priority(fields: dict[str, Any], text: str) -> int:
    if fields.get("priority"):
        return int(fields["priority"])
    blob = f"{fields.get('bic_type', '')} {fields.get('paper_role', '')} {text[:4000]}".lower()
    if any(t in blob for t in ("core", "topological", "symmetry-protected", "quasi-bic", "bic laser")):
        return 2
    if "supplementary" in blob or "background" in blob:
        return 4
    if "non-bic" in blob:
        return 5
    return 3


def open_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    return conn


def write_hdf5_summary(h5_path: Path, records: list[dict[str, Any]]) -> None:
    h5_path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(h5_path, "w") as h5:
        h5.attrs["created_at"] = utc_now()
        h5.attrs["description"] = "Initial BIC literature HDF5 container. Numeric spectra/geometry arrays will be added during curation."
        for record in records:
            group = h5.create_group(f"papers/{record['paper_id']}")
            group.attrs["file_name"] = record["file_name"]
            group.attrs["title"] = record.get("title") or ""
            group.attrs["sha256"] = record["sha256"]
            text = (record.get("first_pages_text") or "")[:8000]
            group.create_dataset("first_pages_text", data=np.bytes_(text.encode("utf-8", errors="ignore")))
            group.create_group("devices")
            group.create_group("spectra")
            group.create_group("real")
            group.create_group("kspace")


def export_tables(conn: sqlite3.Connection, export_dir: Path) -> None:
    export_dir.mkdir(parents=True, exist_ok=True)
    for table in ("papers", "devices", "evidence", "external_literature"):
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        cols = [desc[0] for desc in conn.execute(f"SELECT * FROM {table} LIMIT 0").description]
        with (export_dir / f"{table}.csv").open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.writer(handle)
            writer.writerow(cols)
            writer.writerows(rows)


def insert_external_seeds(conn: sqlite3.Connection) -> None:
    for seed in EXTERNAL_SEEDS:
        cols = ", ".join(seed.keys())
        placeholders = ", ".join("?" for _ in seed)
        updates = ", ".join(f"{key}=excluded.{key}" for key in seed if key != "external_id")
        conn.execute(
            f"INSERT INTO external_literature ({cols}) VALUES ({placeholders}) "
            f"ON CONFLICT(external_id) DO UPDATE SET {updates}",
            list(seed.values()),
        )


def build_database(source_dir: Path, db_path: Path, h5_path: Path, export_dir: Path, max_pages: int) -> None:
    source_dir = source_dir.resolve()
    pdfs = sorted(source_dir.glob("*.pdf"), key=lambda p: p.name.lower())
    if not pdfs:
        raise SystemExit(f"No PDFs found in {source_dir}")

    conn = open_db(db_path)
    conn.execute("DELETE FROM ingestion_log")
    conn.execute("DELETE FROM novelty_map")
    conn.execute("DELETE FROM external_literature")
    conn.execute("DELETE FROM claims")
    conn.execute("DELETE FROM resonances")
    conn.execute("DELETE FROM spectra")
    conn.execute("DELETE FROM bic_modes")
    conn.execute("DELETE FROM materials")
    conn.execute("DELETE FROM geometry_params")
    conn.execute("DELETE FROM devices")
    conn.execute("DELETE FROM evidence")
    conn.execute("DELETE FROM paper_text")
    conn.execute("DELETE FROM papers")

    records: list[dict[str, Any]] = []
    now = utc_now()
    for index, pdf in enumerate(pdfs, start=1):
        paper_id = f"P{index:04d}"
        evidence_id = f"E{index:04d}-AUTO"
        device_id = f"D{index:04d}-AUTO"
        pdf_hash = sha256_file(pdf)
        extracted = extract_pdf(pdf, max_pages=max_pages)
        text = extracted["text"]
        metadata = extracted["metadata"]
        hint = apply_curated_hint(pdf)
        auto = classify(text, pdf.name)

        fields: dict[str, Any] = {
            "paper_id": paper_id,
            "sha256": pdf_hash,
            "file_name": pdf.name,
            "pdf_path": str(pdf),
            "title": metadata_title(metadata) or first_page_title(text) or filename_title(pdf),
            "authors": clean_text(str(metadata.get("author") or "")) or None,
            "year": extract_year(text, metadata),
            "source": None,
            "doi": extract_doi(f"{pdf.name}\n{text}"),
            "arxiv": extract_arxiv(f"{pdf.name}\n{text}"),
            "paper_role": auto["paper_role"],
            "bic_type": auto["bic_type"],
            "platform": auto["platform"],
            "mechanism": auto["mechanism"],
            "experiment_or_theory": auto["experiment_or_theory"],
            "page_count": extracted["page_count"],
            "priority": None,
            "review_status": "auto_extracted",
            "notes": None,
            "created_at": now,
            "first_pages_text": text,
            "abstract_candidate": abstract_candidate(text),
            "keyword_hits": json.dumps(auto["keyword_hits"], ensure_ascii=False, sort_keys=True),
            "extraction_pages": extracted["pages_read"],
            "extraction_error": extracted["error"],
        }
        fields.update({k: v for k, v in hint.items() if v is not None})
        fields["priority"] = guess_priority(fields, text)
        records.append(fields)

        paper_cols = [
            "paper_id",
            "sha256",
            "file_name",
            "pdf_path",
            "title",
            "authors",
            "year",
            "source",
            "doi",
            "arxiv",
            "paper_role",
            "bic_type",
            "platform",
            "mechanism",
            "experiment_or_theory",
            "page_count",
            "priority",
            "review_status",
            "notes",
            "created_at",
        ]
        conn.execute(
            f"INSERT INTO papers ({', '.join(paper_cols)}) VALUES ({', '.join('?' for _ in paper_cols)})",
            [fields.get(col) for col in paper_cols],
        )
        conn.execute(
            """
            INSERT INTO paper_text
            (paper_id, first_pages_text, abstract_candidate, keyword_hits, extraction_pages, extraction_error, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                paper_id,
                text,
                fields["abstract_candidate"],
                fields["keyword_hits"],
                fields["extraction_pages"],
                fields["extraction_error"],
                now,
            ],
        )
        quote = (fields["abstract_candidate"] or text[:700]).strip()
        conn.execute(
            """
            INSERT INTO evidence
            (evidence_id, paper_id, page, quoted_text, source_kind, evidence_level, confidence, operator, created_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                evidence_id,
                paper_id,
                1,
                quote[:1800],
                "pdf_text_auto",
                "E0",
                0.45 if extracted["error"] else 0.65,
                "build_bic_database.py",
                now,
                "Automatic seed evidence from first pages; requires human curation before numeric use.",
            ],
        )
        conn.execute(
            """
            INSERT INTO devices
            (device_id, paper_id, device_name, geometry_family, application, dimension, periodic_type, fabricated_or_simulated, evidence_id, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                device_id,
                paper_id,
                "auto-seeded main structure",
                fields["platform"],
                None,
                None,
                "periodic" if any(t in (fields["platform"] or "").lower() for t in ("slab", "metasurface", "array", "grating")) else None,
                fields["experiment_or_theory"],
                evidence_id,
                "Placeholder device row for later parameter extraction.",
            ],
        )
        if fields.get("paper_role") or fields.get("bic_type"):
            conn.execute(
                """
                INSERT INTO claims
                (claim_id, paper_id, claim_text, claim_type, structure_family, mechanism, application, evidence_id, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    f"C{index:04d}-AUTO",
                    paper_id,
                    f"{fields.get('bic_type')} in {fields.get('platform')}",
                    "auto_classification",
                    fields.get("platform"),
                    fields.get("mechanism"),
                    None,
                    evidence_id,
                    "Machine-generated classification claim; verify against paper.",
                ],
            )

    insert_external_seeds(conn)
    conn.execute(
        "INSERT INTO ingestion_log (event_time, level, message, details) VALUES (?, ?, ?, ?)",
        [utc_now(), "INFO", f"Ingested {len(records)} local PDFs", json.dumps({"source_dir": str(source_dir)}, ensure_ascii=False)],
    )
    conn.commit()
    write_hdf5_summary(h5_path, records)
    export_tables(conn, export_dir)
    conn.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--h5", type=Path, default=DEFAULT_H5_PATH)
    parser.add_argument("--export-dir", type=Path, default=DEFAULT_EXPORT_DIR)
    parser.add_argument("--max-pages", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_database(args.source_dir, args.db, args.h5, args.export_dir, args.max_pages)
    print(f"Built database: {args.db}")
    print(f"Built HDF5 container: {args.h5}")
    print(f"Exported CSV tables to: {args.export_dir}")


if __name__ == "__main__":
    main()
