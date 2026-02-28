# Spectral Universality in Resting-State Brain Networks

[![bioRxiv](https://img.shields.io/badge/bioRxiv-BIORXIV--2026--707267-blue)](https://www.biorxiv.org/content/10.1101/2026.BIORXIV-707267)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/badge/GitHub-richardschorriii-black)](https://github.com/richardschorriii/brain-spectral-universality)

**Paper 1 of the PMIR Neuroscience Series**

Schorr, R. L. (2026). Spectral Universality in Resting-State Brain Networks: Evidence for Equilibrium Dynamics. *bioRxiv* (BIORXIV-2026-707267).

> **Note on branches:**
> This `main` branch contains Paper 1 only (PhysioNet EEG, N=10).
> Paper 2 (ABIDE 17-site cross-validation, N=872) lives on the [`paper-02` branch](../../tree/paper-02).
> See [BRANCH_STRATEGY.md](BRANCH_STRATEGY.md) for how this series is organized.

---

## Summary

We demonstrate extraordinarily high spectral universality (r = 0.9852, p < 0.000001) in human resting-state brain networks. After rescaling by the spectral gap λ₂, eigenvalue distributions collapse onto a universal spectral structure organized into five distinct frequency bands, 410-fold greater than null model expectations.

**Key findings:**
- 98.5% of spectral variance shared across individuals (r = 0.9852, p < 0.000001)
- 410-fold greater than null model (Z = 262.8)
- Survives Bonferroni correction across all 5 frequency bands
- Generalizes across brain states (eyes-open: r = 0.9555, eyes-closed: r = 0.9852)
- Rescaling-independent — emerges identically across λ₂, λ₃, λ₄, λ_mean, λ_max, and raw eigenvalues
- Robust across connectivity methods (PLV: r = 0.9974, Pearson: r = 0.9902, Coherence: r = 0.8538)
- Independent of individual connectivity topology (ρ = 0.11, p = 0.34)
- Task engagement reduces universality by 25.4% (Δr = −0.2502) — evidence for equilibrium dynamics

---

## Repository Structure

```
brain-spectral-universality/          ← Paper 1 (this branch: main)
│
├── BRANCH_STRATEGY.md                # How the PMIR neuroscience paper series is organized
│
├── code/                             # Analysis scripts
│   ├── config.py                     # All pipeline parameters
│   ├── run_pipeline.py               # Master pipeline orchestrator (9 stages)
│   ├── run_refined_tests.py          # Refined statistical tests
│   ├── run_test_c_all_sites.py       # ABIDE cross-site runner (used in paper-02)
│   ├── download_abide.py             # ABIDE data download helper
│   └── modules/                      # Core analysis modules
│       ├── data_acquisition.py       # Dataset loading
│       ├── spectral_analysis.py      # Laplacian, eigendecomposition, λ₂ rescaling
│       ├── null_models.py            # Configuration model null comparisons
│       └── consciousness_analysis.py # State-dependent analysis
│
├── data/
│   └── processed/                    # Processed results (CSVs)
│       ├── spectral_properties.csv   # Per-subject λ₂ values (N=10, rest + task)
│       ├── band_correlations.csv     # Per-band correlations
│       └── summary_results.csv       # Overall universality metrics
│
├── figures/
│   ├── main/                         # Figures 1–4 (PDF + PNG)
│   └── supplementary/               # Figures S1–S5 (PDF + PNG)
│
├── tables/
│   └── supplementary/               # Tables S1–S4 (CSV)
│
└── manuscript/
    ├── BIORXIV-2026-707267v1-SCHORR.pdf     # Submitted preprint
    └── manuscript_v1.2_FINAL_WITH_REFS.pdf  # With full reference list
```

---

## Quick Start

```bash
git clone https://github.com/richardschorriii/brain-spectral-universality.git
cd brain-spectral-universality
pip install -r requirements.txt

# Configure paths and dataset toggles
nano code/config.py

# Run complete analysis pipeline
python code/run_pipeline.py
```

---

## Data

**Primary dataset — PhysioNet EEG:**
- 64-channel EEG, 160 Hz, N=10 subjects (S001–S010)
- Conditions: eyes-closed rest (R02), eyes-open rest (R01), motor imagery (R04)
- Download: https://physionet.org/content/eegmmidb/1.0.0/

Raw data not included (too large for GitHub). Processed results in `data/processed/`.

---

## Main Results

| Metric | Value |
|--------|-------|
| Overall universality | r = 0.9852 |
| Band 1 | r = 0.9935 |
| Band 2 | r = 0.9941 |
| Band 3 | r = 0.9932 |
| Band 4 | r = 0.9967 |
| Band 5 | r = 0.9485 |
| Null model | r = 0.0024 |
| Improvement over null | 410× (p < 0.000001) |
| Task perturbation | Δr = −0.2502 (25.4% decrease) |
| Topology independence | ρ = 0.11, p = 0.34 |

---

## Figures

| Figure | Description |
|--------|-------------|
| Figure 1 | λ₂ distribution — resting state, per-subject, rest vs. task |
| Figure 2 | Spectral universality — band correlations, pairwise distribution |
| Figure 3 | Null model comparison and band sensitivity analysis |
| Figure 4 | Topology independence — spectral vs. connectivity similarity |

Supplementary (S1–S5): null model detail, band sensitivity, eyes-open comparison, rescaling parameter comparison, connectivity methods comparison.

---

## Theoretical Framework

This paper applies the **Phase-Modulated Information Rivalry (PMIR)** framework to neuroscience, demonstrating that resting brain networks exist in a universal equilibrium state characterized by λ₂-organized spectral structure.

For PMIR theoretical foundations and cross-domain applications:
- Schorr, R. L. (2026). Chaos onset in N-body systems. *Zenodo*. https://doi.org/10.5281/zenodo.18652630
- Schorr, R. L. (2026). Hubble tension and observation-induced frame dependence. *Zenodo*. https://doi.org/10.5281/zenodo.18652539

---

## PMIR Neuroscience Paper Series

| Branch | Paper | Status |
|--------|-------|--------|
| `main` | **Paper 1:** Spectral universality in resting-state EEG (PhysioNet, N=10) | Under review |
| `paper-02` | **Paper 2:** ABIDE 17-site cross-validation (N=872) | In preparation |

See [BRANCH_STRATEGY.md](BRANCH_STRATEGY.md) for planned future papers.

---

## Citation

```bibtex
@article{Schorr2026spectral,
  title={Spectral Universality in Resting-State Brain Networks: Evidence for Equilibrium Dynamics},
  author={Schorr, Richard L.},
  journal={bioRxiv},
  year={2026},
  note={BIORXIV-2026-707267}
}
```

---

## Contact

**Richard L. Schorr III** — Independent Researcher, Lancaster, Ohio, USA
richardschorriii@gmail.com | https://github.com/richardschorriii

---

## Acknowledgments

- PhysioNet / Schalk et al. (2004) for the EEG Motor Movement/Imagery Dataset
- Open-source neuroscience community

*License: MIT. Last updated: February 2026.*
