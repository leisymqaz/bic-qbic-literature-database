PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS source_files (
    file_id TEXT PRIMARY KEY,
    file_name TEXT NOT NULL,
    pdf_path TEXT NOT NULL,
    sha256 TEXT UNIQUE NOT NULL,
    size_bytes INTEGER NOT NULL,
    page_count INTEGER,
    pdf_metadata_title TEXT,
    pdf_metadata_author TEXT,
    pdf_metadata_subject TEXT,
    pdf_metadata_keywords TEXT,
    extraction_status TEXT NOT NULL,
    extraction_error TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS papers (
    paper_id TEXT PRIMARY KEY,
    file_id TEXT NOT NULL REFERENCES source_files(file_id) ON DELETE CASCADE,
    title TEXT,
    title_source TEXT,
    doi TEXT,
    doi_source TEXT,
    arxiv TEXT,
    arxiv_source TEXT,
    year INTEGER,
    year_source TEXT,
    source TEXT,
    source_source TEXT,
    crossref_title TEXT,
    crossref_container TEXT,
    crossref_year INTEGER,
    crossref_url TEXT,
    verification_status TEXT NOT NULL,
    curation_status TEXT NOT NULL DEFAULT 'machine_extracted_needs_review',
    duplicate_of TEXT REFERENCES papers(paper_id),
    supplement_to TEXT REFERENCES papers(paper_id),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS evidence (
    evidence_id TEXT PRIMARY KEY,
    paper_id TEXT REFERENCES papers(paper_id) ON DELETE CASCADE,
    file_id TEXT REFERENCES source_files(file_id) ON DELETE CASCADE,
    source_kind TEXT NOT NULL,
    source_path TEXT,
    source_url TEXT,
    page_start INTEGER,
    page_end INTEGER,
    figure TEXT,
    panel TEXT,
    table_no TEXT,
    equation_no TEXT,
    quote TEXT,
    quote_sha256 TEXT,
    extraction_method TEXT NOT NULL,
    evidence_level TEXT NOT NULL,
    confidence REAL,
    verification_status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS candidate_classifications (
    candidate_id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(paper_id) ON DELETE CASCADE,
    candidate_field TEXT NOT NULL,
    candidate_value TEXT,
    evidence_id TEXT REFERENCES evidence(evidence_id),
    method TEXT NOT NULL,
    verification_status TEXT NOT NULL DEFAULT 'candidate_needs_human_review',
    confidence REAL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS external_verified_papers (
    external_id TEXT PRIMARY KEY,
    title TEXT,
    year INTEGER,
    source TEXT,
    doi TEXT,
    arxiv TEXT,
    url TEXT NOT NULL,
    source_kind TEXT NOT NULL,
    verification_status TEXT NOT NULL,
    checked_at TEXT NOT NULL,
    relevance_scope TEXT,
    overlap_risk TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS devices (
    device_id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(paper_id) ON DELETE CASCADE,
    device_name TEXT,
    geometry_family TEXT,
    evidence_id TEXT NOT NULL REFERENCES evidence(evidence_id),
    verification_status TEXT NOT NULL,
    curation_status TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS resonances (
    resonance_id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(paper_id) ON DELETE CASCADE,
    device_id TEXT REFERENCES devices(device_id),
    lambda0_nm REAL,
    q_factor REAL,
    linewidth_nm REAL,
    gamma REAL,
    fano_q REAL,
    fit_formula TEXT,
    extraction_method TEXT NOT NULL,
    digitization_uncertainty TEXT,
    evidence_id TEXT NOT NULL REFERENCES evidence(evidence_id),
    verification_status TEXT NOT NULL,
    curation_status TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS physical_observations (
    observation_id TEXT PRIMARY KEY,
    paper_id TEXT REFERENCES papers(paper_id) ON DELETE CASCADE,
    external_id TEXT REFERENCES external_verified_papers(external_id) ON DELETE CASCADE,
    file_id TEXT REFERENCES source_files(file_id) ON DELETE CASCADE,
    observation_group TEXT NOT NULL,
    observation_type TEXT NOT NULL,
    quantity_name TEXT,
    value_text TEXT,
    value_numeric REAL,
    unit TEXT,
    material TEXT,
    structure_name TEXT,
    wavelength_nm REAL,
    frequency_thz REAL,
    q_factor REAL,
    fano_q REAL,
    source_kind TEXT NOT NULL,
    source_url TEXT,
    page INTEGER,
    figure TEXT,
    panel TEXT,
    table_no TEXT,
    quote TEXT NOT NULL,
    evidence_id TEXT REFERENCES evidence(evidence_id),
    extraction_method TEXT NOT NULL,
    verification_status TEXT NOT NULL,
    curation_status TEXT NOT NULL,
    confidence REAL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS web_sources (
    web_source_id TEXT PRIMARY KEY,
    title TEXT,
    url TEXT NOT NULL UNIQUE,
    doi TEXT,
    year INTEGER,
    publisher TEXT,
    source_kind TEXT NOT NULL,
    checked_at TEXT NOT NULL,
    accessible_text_excerpt TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS audit_log (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_time TEXT NOT NULL,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    details TEXT
);

CREATE INDEX IF NOT EXISTS idx_verified_papers_doi ON papers(doi);
CREATE INDEX IF NOT EXISTS idx_verified_papers_status ON papers(verification_status);
CREATE INDEX IF NOT EXISTS idx_verified_evidence_paper ON evidence(paper_id);
CREATE INDEX IF NOT EXISTS idx_candidate_classifications_paper ON candidate_classifications(paper_id);
CREATE INDEX IF NOT EXISTS idx_physical_observations_paper ON physical_observations(paper_id);
CREATE INDEX IF NOT EXISTS idx_physical_observations_type ON physical_observations(observation_type);
