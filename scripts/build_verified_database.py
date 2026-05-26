#!/usr/bin/env python
"""Build a verified-only seed database from local BIC PDFs.

The output separates source-backed facts from candidates. Heuristic BIC type,
platform, and mechanism labels go only into candidate_classifications and are
not treated as verified paper facts.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import fitz
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyMuPDF is required: install package 'pymupdf'.") from exc


PROJECT_DIR = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_DIR / "schema_verified.sql"
DEFAULT_SOURCE_DIR = Path("pdfs")
DEFAULT_DB_PATH = PROJECT_DIR / "data" / "bic_literature_verified.sqlite"
DEFAULT_EXPORT_PATH = PROJECT_DIR / "reports" / "verified_database_inventory.md"

DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
ARXIV_RE = re.compile(r"(?:arXiv:?\s*)?(\d{4}\.\d{4,5})(?:v\d+)?", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(19[7-9]\d|20[0-2]\d)\b")


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_bytes(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean(text: str) -> str:
    text = html.unescape(text)
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf(path: Path, max_pages: int) -> dict[str, Any]:
    out: dict[str, Any] = {
        "metadata": {},
        "page_count": None,
        "pages": [],
        "status": "ok",
        "error": None,
    }
    try:
        doc = fitz.open(path)
        out["metadata"] = doc.metadata or {}
        out["page_count"] = doc.page_count
        for i in range(min(max_pages, doc.page_count)):
            out["pages"].append(clean(doc.load_page(i).get_text("text")))
        doc.close()
    except Exception as exc:  # pragma: no cover
        out["status"] = "error"
        out["error"] = repr(exc)
    return out


def find_with_page(pattern: re.Pattern[str], pages: list[str]) -> tuple[str | None, int | None, str | None]:
    for index, page_text in enumerate(pages, start=1):
        match = pattern.search(page_text)
        if match:
            value = match.group(0) if pattern is DOI_RE else match.group(1)
            value = value.rstrip(".,;:)\\]}>")
            start = max(match.start() - 160, 0)
            end = min(match.end() + 160, len(page_text))
            return value, index, clean(page_text[start:end])
    return None, None, None


def title_candidates(pages: list[str], metadata: dict[str, Any], file_name: str) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    meta_title = clean(str(metadata.get("title") or ""))
    if len(meta_title) >= 8 and "microsoft" not in meta_title.lower() and meta_title.lower() != "untitled":
        candidates.append({"value": meta_title, "source": "pdf_metadata:title", "page": None, "quote": meta_title})

    if pages:
        lines = [clean(line) for line in pages[0].splitlines()]
        skip = ("---", "abstract", "introduction", "copyright", "downloaded", "arxiv", "doi:", "www.", "licensed")
        for line in lines[:80]:
            if not (12 <= len(line) <= 220):
                continue
            lower = line.lower()
            if any(token in lower for token in skip):
                continue
            if len(line.split()) < 3:
                continue
            if re.fullmatch(r"[\d\s.,;:()-]+", line):
                continue
            candidates.append({"value": line, "source": "pdf_page_1_text_candidate", "page": 1, "quote": line})
            break

    stem = clean(re.sub(r"[_@]+", " ", Path(file_name).stem))
    candidates.append({"value": stem, "source": "file_name_candidate", "page": None, "quote": stem})
    return candidates


def year_candidate(pages: list[str], metadata: dict[str, Any]) -> tuple[int | None, str | None, int | None, str | None]:
    date_text = " ".join(str(metadata.get(k, "")) for k in ("creationDate", "modDate"))
    years = [int(y) for y in YEAR_RE.findall(date_text) if 1970 <= int(y) <= 2026]
    if years:
        return years[0], "pdf_metadata_date", None, date_text
    for index, page_text in enumerate(pages, start=1):
        page_years = [int(y) for y in YEAR_RE.findall(page_text[:5000]) if 1970 <= int(y) <= 2026]
        if page_years:
            year = min(page_years)
            match = re.search(str(year), page_text)
            quote = page_text[max((match.start() if match else 0) - 120, 0) : (match.end() if match else 0) + 120]
            return year, "pdf_text_candidate", index, clean(quote)
    return None, None, None, None


def crossref_lookup(doi: str, timeout: int = 15) -> dict[str, Any] | None:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    req = urllib.request.Request(url, headers={"User-Agent": "bic-literature-project/0.1 (mailto:research@example.invalid)"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status != 200:
                return None
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None
    msg = payload.get("message", {})
    title = (msg.get("title") or [None])[0]
    container = (msg.get("container-title") or [None])[0]
    issued = msg.get("issued", {}).get("date-parts", [[None]])
    year = issued[0][0] if issued and issued[0] else None
    return {
        "title": clean(title or "") or None,
        "container": clean(container or "") or None,
        "year": year,
        "url": msg.get("URL") or f"https://doi.org/{doi}",
    }


def title_similarity(a: str | None, b: str | None) -> float:
    if not a or not b:
        return 0.0
    norm_a = re.sub(r"[^a-z0-9]+", " ", a.lower()).strip()
    norm_b = re.sub(r"[^a-z0-9]+", " ", b.lower()).strip()
    if not norm_a or not norm_b:
        return 0.0
    return SequenceMatcher(None, norm_a, norm_b).ratio()


def candidate_labels(file_name: str, pages: list[str]) -> list[tuple[str, str, float]]:
    blob = f"{file_name}\n" + "\n".join(pages[:2])
    lower = blob.lower()
    labels: list[tuple[str, str, float]] = []
    rules = [
        ("suggested_bic_type", "topological / polarization-vortex BIC", ["topological", "polarization vortex", "vortex"], 0.55),
        ("suggested_bic_type", "symmetry-protected BIC", ["symmetry-protected", "symmetry protected", "symmetry-guaranteed"], 0.55),
        ("suggested_bic_type", "quasi-BIC / Fano resonance", ["quasi-bound", "quasi-bic", "fano"], 0.50),
        ("suggested_bic_type", "BIC laser / quasi-BIC laser", ["lasing", "laser"], 0.45),
        ("suggested_platform", "photonic crystal slab", ["photonic crystal slab", "phc slab"], 0.55),
        ("suggested_platform", "metasurface", ["metasurface"], 0.55),
        ("suggested_platform", "dielectric grating", ["grating"], 0.45),
        ("suggested_platform", "waveguide array", ["waveguide array"], 0.45),
        ("suggested_mechanism", "Friedrich-Wintgen/interfering resonances", ["friedrich", "interfering resonances"], 0.50),
        ("suggested_mechanism", "topological charge / momentum-space vortex", ["topological charge", "polarization vortex"], 0.55),
    ]
    for field, value, tokens, confidence in rules:
        if any(token in lower for token in tokens):
            labels.append((field, value, confidence))
    return labels


def open_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    return conn


def reset_tables(conn: sqlite3.Connection) -> None:
    for table in [
        "audit_log",
        "resonances",
        "devices",
        "external_verified_papers",
        "candidate_classifications",
        "evidence",
        "papers",
        "source_files",
    ]:
        conn.execute(f"DELETE FROM {table}")


def insert_evidence(
    conn: sqlite3.Connection,
    evidence_id: str,
    paper_id: str | None,
    file_id: str,
    source_kind: str,
    source_path: str,
    page: int | None,
    quote: str | None,
    method: str,
    level: str,
    status: str,
    confidence: float,
    notes: str | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO evidence
        (evidence_id, paper_id, file_id, source_kind, source_path, page_start, page_end, quote,
         quote_sha256, extraction_method, evidence_level, confidence, verification_status, created_at, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            evidence_id,
            paper_id,
            file_id,
            source_kind,
            source_path,
            page,
            page,
            quote,
            sha256_bytes(quote or ""),
            method,
            level,
            confidence,
            status,
            now_utc(),
            notes,
        ],
    )


def build(source_dir: Path, db_path: Path, max_pages: int, crossref: bool, polite_delay: float) -> None:
    pdfs = sorted(source_dir.glob("*.pdf"), key=lambda p: p.name.lower())
    if not pdfs:
        raise SystemExit(f"No PDFs found in {source_dir}")
    conn = open_db(db_path)
    reset_tables(conn)
    now = now_utc()

    for idx, pdf in enumerate(pdfs, start=1):
        file_id = f"F{idx:04d}"
        paper_id = f"P{idx:04d}"
        extracted = extract_pdf(pdf, max_pages=max_pages)
        metadata = extracted["metadata"]
        pages = extracted["pages"]
        conn.execute(
            """
            INSERT INTO source_files
            (file_id, file_name, pdf_path, sha256, size_bytes, page_count, pdf_metadata_title,
             pdf_metadata_author, pdf_metadata_subject, pdf_metadata_keywords, extraction_status,
             extraction_error, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                file_id,
                pdf.name,
                str(pdf),
                sha256_file(pdf),
                pdf.stat().st_size,
                extracted["page_count"],
                clean(str(metadata.get("title") or "")) or None,
                clean(str(metadata.get("author") or "")) or None,
                clean(str(metadata.get("subject") or "")) or None,
                clean(str(metadata.get("keywords") or "")) or None,
                extracted["status"],
                extracted["error"],
                now,
            ],
        )

        text_joined = "\n\n".join(pages)
        doi, doi_page, doi_quote = find_with_page(DOI_RE, pages)
        arxiv, arxiv_page, arxiv_quote = find_with_page(ARXIV_RE, pages)
        year, year_source, year_page, year_quote = year_candidate(pages, metadata)
        titles = title_candidates(pages, metadata, pdf.name)
        chosen_title = titles[0]["value"] if titles else None
        chosen_title_source = titles[0]["source"] if titles else None

        crossref_data = None
        if crossref and doi:
            crossref_data = crossref_lookup(doi)
            time.sleep(polite_delay)

        title_match_score = None
        verification_status = "local_pdf_indexed"
        if doi and crossref_data:
            title_match_score = title_similarity(chosen_title, crossref_data.get("title"))
            if title_match_score >= 0.62:
                verification_status = "doi_crossref_resolved_title_match"
            else:
                verification_status = "doi_crossref_resolved_title_mismatch_needs_review"
        elif doi:
            verification_status = "doi_extracted_from_pdf_needs_review"

        conn.execute(
            """
            INSERT INTO papers
            (paper_id, file_id, title, title_source, doi, doi_source, arxiv, arxiv_source,
             year, year_source, source, source_source, crossref_title, crossref_container,
             crossref_year, crossref_url, verification_status, curation_status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                paper_id,
                file_id,
                chosen_title,
                chosen_title_source,
                doi,
                f"pdf_page_{doi_page}" if doi_page else None,
                arxiv,
                f"pdf_page_{arxiv_page}" if arxiv_page else None,
                year,
                year_source,
                crossref_data.get("container") if crossref_data else None,
                "crossref" if crossref_data and crossref_data.get("container") else None,
                crossref_data.get("title") if crossref_data else None,
                crossref_data.get("container") if crossref_data else None,
                crossref_data.get("year") if crossref_data else None,
                crossref_data.get("url") if crossref_data else None,
                verification_status,
                "machine_extracted_needs_review",
                f"Only source-file facts are direct facts. DOI/Crossref metadata requires title-match review. title_match_score={title_match_score}",
            ],
        )

        first_quote = clean(text_joined[:1800]) if text_joined else None
        insert_evidence(
            conn,
            f"E{idx:04d}-TEXT",
            paper_id,
            file_id,
            "pdf_text_cache",
            str(pdf),
            1 if first_quote else None,
            first_quote,
            "pymupdf_first_pages",
            "E0",
            "source_extracted_needs_review",
            0.60 if first_quote else 0.0,
            "Automatic text cache for search and later human review.",
        )
        if doi and doi_quote:
            insert_evidence(
                conn,
                f"E{idx:04d}-DOI",
                paper_id,
                file_id,
                "pdf_text_identifier",
                str(pdf),
                doi_page,
                doi_quote,
                "regex_doi_from_pdf_text",
                "E1",
                "identifier_extracted_needs_review",
                0.80,
                "Identifier string found in local PDF text; Crossref resolution stored separately when available.",
            )
        if arxiv and arxiv_quote:
            insert_evidence(
                conn,
                f"E{idx:04d}-ARXIV",
                paper_id,
                file_id,
                "pdf_text_identifier",
                str(pdf),
                arxiv_page,
                arxiv_quote,
                "regex_arxiv_from_pdf_text",
                "E1",
                "identifier_extracted_needs_review",
                0.75,
                "arXiv identifier string found in local PDF text.",
            )
        if chosen_title:
            insert_evidence(
                conn,
                f"E{idx:04d}-TITLE",
                paper_id,
                file_id,
                "pdf_metadata_or_page_text",
                str(pdf),
                titles[0]["page"],
                titles[0]["quote"],
                chosen_title_source or "title_candidate",
                "E0" if "candidate" in (chosen_title_source or "") else "E1",
                "title_candidate_needs_review",
                0.55 if "candidate" in (chosen_title_source or "") else 0.70,
                "Title candidate; verify against title page or Crossref before using in final bibliography.",
            )
        if year and year_quote:
            insert_evidence(
                conn,
                f"E{idx:04d}-YEAR",
                paper_id,
                file_id,
                "pdf_metadata_or_page_text",
                str(pdf),
                year_page,
                year_quote,
                year_source or "year_candidate",
                "E0",
                "year_candidate_needs_review",
                0.45,
                "Year candidate from metadata/text; prefer Crossref year when DOI resolves.",
            )

        for c_idx, (field, value, confidence) in enumerate(candidate_labels(pdf.name, pages), start=1):
            conn.execute(
                """
                INSERT INTO candidate_classifications
                (candidate_id, paper_id, candidate_field, candidate_value, evidence_id, method,
                 verification_status, confidence, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    f"C{idx:04d}-{c_idx:02d}",
                    paper_id,
                    field,
                    value,
                    f"E{idx:04d}-TEXT",
                    "keyword_candidate_from_file_and_first_pages",
                    "candidate_needs_human_review",
                    confidence,
                    "Not a verified fact. Promote only after page/figure/text review.",
                ],
            )

    conn.execute(
        "INSERT INTO audit_log (event_time, level, message, details) VALUES (?, ?, ?, ?)",
        [
            now_utc(),
            "INFO",
            "Built verified-only seed database",
            json.dumps({"source_dir": str(source_dir), "pdf_count": len(pdfs), "crossref": crossref}, ensure_ascii=False),
        ],
    )
    conn.commit()
    conn.close()


def report(db_path: Path, out_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    total = conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
    doi_count = conn.execute("SELECT COUNT(*) FROM papers WHERE doi IS NOT NULL").fetchone()[0]
    crossref_count = conn.execute("SELECT COUNT(*) FROM papers WHERE verification_status='doi_crossref_resolved_title_match'").fetchone()[0]
    evidence_counts = conn.execute("SELECT evidence_level, COUNT(*) n FROM evidence GROUP BY evidence_level").fetchall()
    status_counts = conn.execute("SELECT verification_status, COUNT(*) n FROM papers GROUP BY verification_status").fetchall()
    samples = conn.execute(
        """
        SELECT p.paper_id, sf.file_name, p.title, p.doi, p.crossref_title, p.crossref_year, p.verification_status
        FROM papers p JOIN source_files sf USING(file_id)
        ORDER BY p.paper_id
        LIMIT 20
        """
    ).fetchall()
    lines = [
        "# Verified-Only BIC Literature Inventory",
        "",
        "This report is intentionally conservative. Candidate BIC types, platforms, devices, mechanisms, and numeric resonances are not treated as facts until manually verified with evidence.",
        "",
        f"- Papers/source PDFs indexed: {total}",
        f"- DOI strings extracted from local PDFs: {doi_count}",
        f"- DOI records resolved through Crossref: {crossref_count}",
        "",
        "## Paper Verification Status",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    lines += [f"| {r['verification_status']} | {r['n']} |" for r in status_counts]
    lines += ["", "## Evidence Level Counts", "", "| Level | Count |", "| --- | ---: |"]
    lines += [f"| {r['evidence_level']} | {r['n']} |" for r in evidence_counts]
    lines += [
        "",
        "## First 20 Indexed Records",
        "",
        "| ID | File | Local title candidate | DOI | Crossref title | Crossref year | Status |",
        "| --- | --- | --- | --- | --- | ---: | --- |",
    ]
    for r in samples:
        row = [r["paper_id"], r["file_name"], r["title"], r["doi"], r["crossref_title"], r["crossref_year"], r["verification_status"]]
        safe = [str(x or "").replace("|", "\\|").replace("\n", " ") for x in row]
        lines.append("| " + " | ".join(safe) + " |")
    lines += [
        "",
        "## Use Rules",
        "",
        "- `source_files` facts such as file name, path, SHA256, size, and page count are source-index facts.",
        "- `papers.doi` is an extracted identifier; prefer rows with `doi_crossref_resolved_title_match` for bibliography work.",
        "- `doi_crossref_resolved_title_mismatch_needs_review` usually means the regex captured a reference DOI, not the paper DOI.",
        "- `candidate_classifications` are not facts. They are review queues.",
        "- `devices` and `resonances` are empty until page/figure/table evidence is curated.",
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    conn.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_EXPORT_PATH)
    parser.add_argument("--max-pages", type=int, default=5)
    parser.add_argument("--no-crossref", action="store_true")
    parser.add_argument("--polite-delay", type=float, default=0.1)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build(args.source_dir, args.db, args.max_pages, not args.no_crossref, args.polite_delay)
    report(args.db, args.report)
    print(f"Built verified database: {args.db}")
    print(f"Wrote conservative inventory: {args.report}")


if __name__ == "__main__":
    main()
