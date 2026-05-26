# Verified BIC/qBIC Research Report

## Boundary

This report separates real source-backed data from candidate interpretation. The database currently contains bibliographic/source-file facts and evidence text. It intentionally contains **no verified device rows and no verified resonance/Q/Fano numeric rows** yet, because those require page/figure/table-level curation or digitized spectra with uncertainty.

## Database State

- Source PDFs indexed: 50
- Paper records: 50
- Core papers promoted after local PDF quote/id checks: 13
- DOI/Crossref title-match records not manually promoted: 18
- External prior-art source-link records: 12
- Web source records with physical observations: 4
- Source-quoted physical observation rows: 939
- Verified devices: 0
- Verified resonances: 0

## Paper Verification Status

| Status | Count |
| --- | --- |
| doi_crossref_resolved_title_match | 18 |
| doi_crossref_resolved_title_mismatch_needs_review | 13 |
| manual_pdf_verified_core | 13 |
| local_pdf_indexed | 6 |

## Core Bibliography Verified From Local PDFs

| ID | File | Title | Year | Source | DOI | arXiv | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P0013 | Experimental Observation of Optical Bound States in the Continuum.pdf | Experimental Observation of Optical Bound States in the Continuum | 2011 | Physical Review Letters | 10.1103/PhysRevLett.107.183901 |  | manual_pdf_verified_core |
| P0028 | PhysRevLett.113.037401.pdf | Analytical Perspective for Bound States in the Continuum in Photonic Crystal Slabs | 2014 | Physical Review Letters | 10.1103/PhysRevLett.113.037401 |  | manual_pdf_verified_core |
| P0011 | Embedded Photonic Eigenvalues in 3D Nanostructures.pdf | Embedded Photonic Eigenvalues in 3D Nanostructures | 2014 | Physical Review Letters | 10.1103/PhysRevLett.112.213903 |  | manual_pdf_verified_core |
| P0030 | PRL2014-BIC拓扑.pdf | Topological Nature of Optical Bound States in the Continuum | 2014 | Physical Review Letters | 10.1103/PhysRevLett.113.257401 |  | manual_pdf_verified_core |
| P0042 | srep-Formation mechanism of guided resonances and BIC in photonic crystal slab.pdf | Formation mechanism of guided resonances and bound states in the continuum in photonic crystal slabs | 2016 | Scientific Reports | 10.1038/srep31908 |  | manual_pdf_verified_core |
| P0008 | Bound states within the radiation continuum in diffraction grating and the role of leaky modes.pdf | Bound states within the radiation continuum in diffraction gratings and the role of leaky modes | 2017 | New Journal of Physics | 10.1088/1367-2630/aa849f |  | manual_pdf_verified_core |
| P0023 | Nature2017-Lasing action from photonic bound states in continum.pdf | Lasing action from photonic bound states in continuum | 2017 | Nature | 10.1038/nature20799 |  | manual_pdf_verified_core |
| P0050 | 没看Light enhancement by quasi-bound states in.pdf | Light enhancement by quasi-bound states in the continuum in dielectric arrays | 2017 | Optics Express | 10.1364/OE.25.014134 |  | manual_pdf_verified_core |
| P0031 | Quasi Bound States in the Continuum with Few Unit.pdf | Quasi Bound States in the Continuum with Few Unit Cells of Photonic Crystal Slab | 2017 | arXiv preprint / Optica template needs verification |  | 1705.09842 | manual_pdf_verified_core |
| P0002 | 1909.12618.pdf | Generating optical vortex beams by momentum-space polarization vortices centered at bound states in the continuum | 2019 | arXiv preprint |  | 1909.12618 | manual_pdf_verified_core |
| P0003 | [Nanophotonics] Nonradiating photonics with resonant dielectric nanostructures.pdf | Nonradiating photonics with resonant dielectric nanostructures | 2019 | Nanophotonics | 10.1515/nanoph-2019-0024 |  | manual_pdf_verified_core |
| P0024 | NC2022-简并BIC.pdf | Realizing symmetry-guaranteed pairs of bound states in the continuum in metasurfaces | 2022 | Nature Communications | 10.1038/s41467-022-35246-w |  | manual_pdf_verified_core |
| P0035 | s41467-023-41068-1.pdf | Twisted moire photonic crystal enabled optical vortex generation through bound states in the continuum | 2023 | Nature Communications | 10.1038/s41467-023-41068-1 |  | manual_pdf_verified_core |

## Candidate Classifications Are Not Facts

The following are review queues only. They should guide manual reading, not be cited as database facts.

| Candidate field | Candidate value | Count |
| --- | --- | --- |
| suggested_bic_type | BIC laser / quasi-BIC laser | 28 |
| suggested_bic_type | quasi-BIC / Fano resonance | 18 |
| suggested_bic_type | topological / polarization-vortex BIC | 17 |
| suggested_bic_type | symmetry-protected BIC | 11 |
| suggested_mechanism | topological charge / momentum-space vortex | 10 |
| suggested_mechanism | Friedrich-Wintgen/interfering resonances | 10 |
| suggested_platform | photonic crystal slab | 17 |
| suggested_platform | dielectric grating | 15 |
| suggested_platform | metasurface | 7 |
| suggested_platform | waveguide array | 4 |

## Verified External Prior-Art Risk

| Title | Year | Source | DOI/arXiv | Risk | Source link | Blocked claim |
| --- | --- | --- | --- | --- | --- | --- |
| Strategical Deep Learning for Photonic Bound States in the Continuum | 2022 | Laser & Photonics Reviews | 10.1002/lpor.202100658; arXiv:2105.03001 | very_high | https://doi.org/10.1002/lpor.202100658 | Blocks broad claims of first physics-informed or resonance-informed deep learning for photonic BIC spectra/inverse design. |
| Machine learning method for predicting line-shapes of Fano resonances induced by bound states in the continuum | 2025 | Scientific Reports | 10.1038/s41598-025-16192-1; arXiv:2504.08409 | very_high | https://www.nature.com/articles/s41598-025-16192-1 | Blocks broad claims of first ML prediction of BIC-induced Fano line shape or Fano parameters. |
| Transformer-Enabled Intelligent Design of High-Q Quasi-BIC Metasurface for Molecular Vibrational Fingerprinting | 2026 | Photonics Research | 10.1364/PRJ.578302 | very_high | https://doi.org/10.1364/PRJ.578302 | Blocks broad claims of first transformer/ViT high-Q qBIC metasurface spectral prediction or inverse design. |
| Infrared bound states in the continuum: random forest method | 2023 | Optics Letters | 10.1364/OL.494629 | high | https://opg.optica.org/ol/abstract.cfm?URI=ol-48-17-4460 | Blocks broad claims of first ML prediction of BIC frequency/subband. |
| Inverse design of all-dielectric metasurfaces with accidental bound states in the continuum | 2023 | Nanophotonics | 10.1515/nanoph-2023-0373; arXiv:2305.10020 | high | https://doi.org/10.1515/nanoph-2023-0373 | Blocks broad claims of first all-dielectric BIC inverse design. |
| Meta-Attention Deep Learning for Smart Development of Metasurface Sensors | 2024 | Advanced Science | 10.1002/advs.202405750 | high | https://doi.org/10.1002/advs.202405750 | Blocks broad claims of first explainable/attention deep learning for high-Q metasurface spectra. |
| Inverse design of polarization-insensitive all-dielectric BIC metasurface with dual Fano-resonances by deep learning | 2025 | Optics Communications | 10.1016/j.optcom.2025.131964 | high | https://doi.org/10.1016/j.optcom.2025.131964 | Blocks broad claims of first deep-learning inverse design for complete qBIC/Fano spectra. |
| Ultrahigh-Q guided mode resonances in an all-dielectric metasurface | 2023 | Nature Communications | 10.1038/s41467-023-39227-5 | result_database_source | https://www.nature.com/articles/s41467-023-39227-5 | Web source added beyond local 50 PDFs. |
| Million-Q free space meta-optical resonator at near-visible wavelengths | 2024 | Nature Communications | 10.1038/s41467-024-54775-0 | result_database_source | https://www.nature.com/articles/s41467-024-54775-0 | Web source added beyond local 50 PDFs. |
| Trapping light in air with membrane metasurfaces for vibrational strong coupling | 2024 | Nature Communications | 10.1038/s41467-024-54284-0 | result_database_source | https://www.nature.com/articles/s41467-024-54284-0 | Web source added beyond local 50 PDFs. |
| Near-field probing of the local density of optical states enhanced by bound states in the continuum in nonlocal metasurfaces | 2025 | Nature Communications | 10.1038/s41467-025-66653-4 | result_database_source | https://www.nature.com/articles/s41467-025-66653-4 | Web source added beyond local 50 PDFs. |
| Reality-infused deep learning for angle-resolved quasi-optical Fourier surfaces | 2026 | PhotoniX | 10.1186/s43074-026-00238-2 | high_adjacent | https://link.springer.com/article/10.1186/s43074-026-00238-2 | Strong adjacent risk for Fourier/k-space, angle-resolved metasurface spectra, and deep learning claims. |

## Physical Observation Review Queue

These rows are the central database object for the user's requested physics data: structure parameters, materials, Q, wavelength/frequency, Fano, linewidth, spectra, k-space, band structure, and polarization/topology. Rows are source-quoted and reviewable, but most are not yet human-verified.

| Source kind | Observation type | Count |
| --- | --- | --- |
| local_pdf_text | material | 285 |
| local_pdf_text | band_structure | 188 |
| local_pdf_text | polarization | 178 |
| local_pdf_text | k_space | 114 |
| local_pdf_text | spectrum | 83 |
| local_pdf_text | q_factor | 38 |
| local_pdf_text | wavelength | 12 |
| local_pdf_text | thickness | 9 |
| local_pdf_text | diameter | 7 |
| local_pdf_text | radius | 4 |
| local_pdf_text | period | 3 |
| local_pdf_text | frequency | 3 |
| web_article_text | q_factor | 4 |
| web_article_text | frequency | 3 |
| web_article_text | scaling_law | 2 |
| web_article_text | geometry_parameter | 2 |
| web_article_text | q_factor_definition | 1 |
| web_article_text | momentum_space_spectroscopy | 1 |
| web_article_text | material | 1 |
| web_article_text | linewidth | 1 |

## Web-Source Physical Observations Added Beyond Local PDFs

| Quantity | Value | Material/structure | Quote | Source URL | Note |
| --- | --- | --- | --- | --- | --- |
| Q factor | 2.39 × 10^5 |  | The experimental results show that the Q-factor was as high as 2.39 × 10^{5}, comparable to the maximum Q-factor of topological BICs. | https://www.nature.com/articles/s41467-023-39227-5 | Nature Communications article text lines 95-98 |
| material/platform | low-index photoresist on SOI waveguide | photoresist; SOI | Instead of patterning the high-index layer to form a Mie resonator in a unit cell, we introduced an ultrathin photoresist layer as a perturbation layer on top of a multilayer-waveguide system. | https://www.nature.com/articles/s41467-023-39227-5 | Nature Communications article text lines 95-98 |
| Q-alpha scaling | Q ∝ α−2 |  | High Q-factors of GMRs can be easily realized as they are inversely proportional to the perturbation parameter squared (Q ∝ α−2). | https://www.nature.com/articles/s41467-023-39227-5 | Nature Communications article text line 96 |
| qBIC TE Q | 722 |  | We measured a maximum Q-factor of 722 for the qBIC TE mode (Fig. 3d) and 463 for the qBIC TM mode. | https://www.nature.com/articles/s41467-024-54284-0 | Nature Communications article text line 146 |
| qBIC TM Q | 463 |  | We measured a maximum Q-factor of 722 for the qBIC TE mode (Fig. 3d) and 463 for the qBIC TM mode. | https://www.nature.com/articles/s41467-024-54284-0 | Nature Communications article text line 146 |
| Q-alpha scaling | inverse quadratic relationship |  | We also plotted the FTIR-measured and simulation-estimated Q-factor values of the qBIC TE mode and observed an inverse quadratic relationship between Q and the asymmetry parameter α. | https://www.nature.com/articles/s41467-024-54284-0 | Nature Communications article text line 147 |
| FWHM | ~13 cm−1 average |  | The average FWHM of the fabricated qBIC TM resonances shown in Fig. 4b is ~ 13 cm−1, i.e., the average loss is 6.5 cm−1. | https://www.nature.com/articles/s41467-024-54284-0 | Nature Communications article text line 151 |
| layer stack and period | 58 nm PMMA / 100 nm SiN / 1470 nm SiO2; P=500 nm; L=50 nm | PMMA; SiN; SiO2; Si | Schematic showing the unit cell ... 58 nm-thick patterned PMMA layer, a 100-nm-thick SiN layer, and a 1470 nm-thick SiO2 layer on a Si substrate. The patterning is defined by the period P and defect hole size L. | https://www.nature.com/articles/s41467-024-54775-0 | Nature Communications article text lines 111-112 |
| Q factor | 1.10 million |  | The Fano fitting (pink curve) reveals a Q factor of 1.10 million. | https://www.nature.com/articles/s41467-024-54775-0 | Nature Communications article text line 174 |
| momentum-space resolved spectroscopy | 0.42 pm/pixel wavelength resolution; 0.028 deg/pixel angle resolution |  | The Γ-point data are extracted from extra-fine laser-scanning momentum-space-resolved reflectance spectroscopy with a wavelength resolution of ~0.42 pm/pixel and an angle resolution of ~0.028 ̊ /pixel. | https://www.nature.com/articles/s41467-024-54775-0 | Nature Communications article text line 174 |
| rod separation | d = 80 μm |  | The inset shows an optical microscope image of a unit cell in the fabricated metasurface, where the separation between the rods is d = 80 μm. | https://www.nature.com/articles/s41467-025-66653-4 | Nature Communications article text line 108 |
| broad even mode frequency | 0.495 THz |  | The broad resonance in the transmission spectrum at 0.495 THz corresponds to the even mode in the array. | https://www.nature.com/articles/s41467-025-66653-4 | Nature Communications article text line 113 |
| off-normal quasi-BIC frequency | 0.365 THz |  | A narrow feature appears in T(ω, θ) around 0.365 THz for off-normal incidence (θ = 40°). | https://www.nature.com/articles/s41467-025-66653-4 | Nature Communications article text line 113 |
| BIC frequency / PLDOS | 0.395 THz |  | The PLDOS enhancement reaches a maximum at the BIC frequency of 0.395 THz for both polarizations and is confined within a height of 20μm from the surface. | https://www.nature.com/articles/s41467-025-66653-4 | Nature Communications article text line 195 |
| Q definition | Q=f0/Δf |  | The symbols represent the extracted quality factor (Q-factor) of the quasi-BIC mode, given by Q = f0/Δf ... retrieved from Fano fitting. | https://www.nature.com/articles/s41467-025-66653-4 | Nature Communications article text line 110 |

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
