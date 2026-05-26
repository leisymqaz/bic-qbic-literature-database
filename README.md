# BIC/qBIC Literature Database

A public, sanitized BIC/qBIC literature database and workflow for traceable photonic bound-state-in-the-continuum research.

This repository is a cleaned publication package generated from a local research workspace. It focuses on database structure, bibliography metadata, evidence bookkeeping, novelty-risk mapping, and reproducible curation scripts.

## What Is Included

- `data/bic_literature_public.sqlite`: sanitized SQLite database.
- `exports_public/*.csv`: sanitized CSV exports from the verified database.
- `docs/schema.sql` and `docs/schema_verified.sql`: original schema references.
- `scripts/*.py`: database build, curation, export, and report scripts.
- `reports/*.md`: project reports and database inventory.

## Sanitization Policy

The public database removes:

- Local PDF files.
- PDF full-text caches.
- Long source quotes and extracted paper text.
- Local absolute paths.
- Private temporary files.

It keeps structured metadata such as paper IDs, title candidates, DOI/arXiv/URL fields where available, evidence levels, page/figure/table fields, SHA-256 hashes, observation categories, verification status, and curation notes.

## Reliability Boundary

Use the public database as a curation scaffold, not as a final ground-truth physical dataset. Many physical-observation rows are candidates that still require manual verification against the original papers.

Evidence levels:

- `E0`: automatic placeholder or unverified extracted text.
- `E1`: direct text/table value from paper.
- `E2`: value converted from paper formula or normalized parameter.
- `E3`: digitized curve value.
- `E4`: estimated from SEM/schematic scale bar.
- `E5`: independently reproduced simulation/experiment.

## Research Position

The safer project framing is:

> Physics-informed Fourier-space learning of quasi-BIC spectra in dielectric metasurfaces, with traceable data, real-space/k-space ablations, cross-topology generalization, and Fourier attribution of radiative coupling.

Avoid claiming broad firsts such as "first ML prediction of qBIC spectra" without a fresh prior-art check.

## Rebuild Notes

The scripts expect a local PDF source folder and may need path configuration before running. The public repository intentionally does not redistribute source PDFs or commercial/copyrighted full text.

## License

Code and database scaffolding are provided under the MIT License. Bibliographic metadata and factual curation records are provided for research use. Source papers remain under their original publishers' licenses.
