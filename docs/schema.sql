PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS papers (
    paper_id TEXT PRIMARY KEY,
    sha256 TEXT UNIQUE NOT NULL,
    file_name TEXT NOT NULL,
    pdf_path TEXT NOT NULL,
    title TEXT,
    authors TEXT,
    year INTEGER,
    source TEXT,
    doi TEXT,
    arxiv TEXT,
    paper_role TEXT,
    bic_type TEXT,
    platform TEXT,
    mechanism TEXT,
    experiment_or_theory TEXT,
    page_count INTEGER,
    priority INTEGER DEFAULT 3,
    review_status TEXT DEFAULT 'auto_extracted',
    notes TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS paper_text (
    paper_id TEXT PRIMARY KEY REFERENCES papers(paper_id) ON DELETE CASCADE,
    first_pages_text TEXT,
    abstract_candidate TEXT,
    keyword_hits TEXT,
    extraction_pages INTEGER,
    extraction_error TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evidence (
    evidence_id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(paper_id) ON DELETE CASCADE,
    page INTEGER,
    figure TEXT,
    panel TEXT,
    table_no TEXT,
    equation_no TEXT,
    caption_text TEXT,
    quoted_text TEXT,
    source_kind TEXT,
    evidence_level TEXT,
    confidence REAL,
    uncertainty TEXT,
    operator TEXT,
    created_at TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS devices (
    device_id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(paper_id) ON DELETE CASCADE,
    device_name TEXT,
    geometry_family TEXT,
    application TEXT,
    dimension TEXT,
    periodic_type TEXT,
    fabricated_or_simulated TEXT,
    evidence_id TEXT REFERENCES evidence(evidence_id),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS geometry_params (
    param_id TEXT PRIMARY KEY,
    device_id TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
    symbol TEXT,
    name TEXT,
    value REAL,
    unit TEXT,
    normalized_value REAL,
    normalized_by TEXT,
    axis TEXT,
    sweep_role TEXT,
    evidence_id TEXT REFERENCES evidence(evidence_id),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS materials (
    material_id TEXT PRIMARY KEY,
    device_id TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
    layer_role TEXT,
    material_name TEXT,
    n REAL,
    k REAL,
    epsilon REAL,
    dispersion_model TEXT,
    thickness REAL,
    unit TEXT,
    source_type TEXT,
    evidence_id TEXT REFERENCES evidence(evidence_id),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS bic_modes (
    mode_id TEXT PRIMARY KEY,
    device_id TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
    bic_type TEXT,
    symmetry_group TEXT,
    mode_label TEXT,
    multipole_label TEXT,
    radiation_channel TEXT,
    topological_charge TEXT,
    symmetry_breaking_param TEXT,
    evidence_id TEXT REFERENCES evidence(evidence_id),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS spectra (
    spectrum_id TEXT PRIMARY KEY,
    device_id TEXT NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
    mode_id TEXT REFERENCES bic_modes(mode_id),
    quantity TEXT,
    x_axis TEXT,
    y_axis TEXT,
    polarization TEXT,
    angle_deg REAL,
    medium_index REAL,
    temperature REAL,
    hdf5_path TEXT,
    raw_source TEXT,
    evidence_id TEXT REFERENCES evidence(evidence_id),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS resonances (
    resonance_id TEXT PRIMARY KEY,
    spectrum_id TEXT NOT NULL REFERENCES spectra(spectrum_id) ON DELETE CASCADE,
    lambda0_nm REAL,
    freq_thz REAL,
    energy_ev REAL,
    q_factor REAL,
    linewidth_nm REAL,
    gamma REAL,
    fano_q REAL,
    amplitude REAL,
    baseline REAL,
    fit_model TEXT,
    fit_error REAL,
    extraction_method TEXT,
    evidence_id TEXT REFERENCES evidence(evidence_id),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS claims (
    claim_id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(paper_id) ON DELETE CASCADE,
    claim_text TEXT,
    claim_type TEXT,
    structure_family TEXT,
    mechanism TEXT,
    application TEXT,
    evidence_id TEXT REFERENCES evidence(evidence_id),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS external_literature (
    external_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    year INTEGER,
    source TEXT,
    doi TEXT,
    arxiv TEXT,
    url TEXT,
    topic TEXT,
    overlap_level TEXT,
    relevance_notes TEXT,
    source_status TEXT DEFAULT 'web_checked'
);

CREATE TABLE IF NOT EXISTS novelty_map (
    idea_id TEXT NOT NULL,
    query TEXT NOT NULL,
    matched_paper_id TEXT,
    matched_external_id TEXT,
    match_type TEXT,
    overlap_score REAL,
    same_geometry INTEGER,
    same_mechanism INTEGER,
    same_target INTEGER,
    risk_level TEXT,
    notes TEXT,
    PRIMARY KEY (idea_id, query, matched_paper_id, matched_external_id)
);

CREATE TABLE IF NOT EXISTS ingestion_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_time TEXT NOT NULL,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    details TEXT
);

CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year);
CREATE INDEX IF NOT EXISTS idx_papers_doi ON papers(doi);
CREATE INDEX IF NOT EXISTS idx_papers_bic_type ON papers(bic_type);
CREATE INDEX IF NOT EXISTS idx_devices_paper_id ON devices(paper_id);
CREATE INDEX IF NOT EXISTS idx_evidence_paper_id ON evidence(paper_id);
CREATE INDEX IF NOT EXISTS idx_resonances_q ON resonances(q_factor);
