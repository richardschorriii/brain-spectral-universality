# Spectral Universality in Resting-State Brain Networks

[![bioRxiv](https://img.shields.io/badge/bioRxiv-preprint-blue)](https://doi.org/YOUR_DOI_HERE)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Code and data for:**  
Schorr, R. L. (2026). Spectral Universality in Resting-State Brain Networks: Evidence for Equilibrium Dynamics. *bioRxiv*. https://doi.org/YOUR_DOI_HERE

---

## Summary

We demonstrate extraordinarily high spectral universality (r = 0.9852, p < 0.000001) in human resting-state brain networks. After rescaling by the spectral gap λ₂, eigenvalue distributions collapse onto a universal spectral structure organized into five distinct frequency bands.

**Key findings:**
- 98.5% of spectral variance shared across individuals
- 410-fold greater than chance (p < 0.000001)
- Survives Bonferroni correction across all frequency bands
- Generalizes across brain states (eyes-open: r = 0.96, eyes-closed: r = 0.99)
- Rescaling-independent universality (all methods yield identical r = 0.9852)
- Robust across connectivity methods (Pearson, PLV, Coherence)
- Independent of individual connectivity topology (ρ = 0.11, p = 0.34)
- Task engagement reduces universality by 25% (evidence for equilibrium dynamics)

---

## Repository Contents

```
brain-spectral-universality/
│
├── code/                      # Analysis scripts
│   ├── preprocessing/         # EEG preprocessing
│   ├── connectivity/          # Connectivity matrix computation
│   ├── spectral_analysis/     # Eigendecomposition & rescaling
│   ├── statistics/            # Correlations & null models
│   └── visualization/         # Figure generation
│
├── data/                      # Data files
│   └── processed/             # Connectivity matrices, eigenvalues
│
├── figures/                   # All manuscript figures
│   ├── main/                  # Figures 1-4
│   └── supplementary/         # Figures S1-S5
│
├── tables/                    # Supplementary tables
│   └── supplementary/         # Tables S1-S4
│
├── manuscript/                # Manuscript files
│   └── preprint_v1.2.pdf      # bioRxiv version
│
└── notebooks/                 # Jupyter notebooks
    ├── exploratory_analysis.ipynb
    └── validation_tests.ipynb
```

---

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/brain-spectral-universality.git
cd brain-spectral-universality

# Install dependencies
pip install -r requirements.txt
```

### Requirements

- Python 3.8+
- NumPy, SciPy, pandas
- MNE-Python (EEG analysis)
- matplotlib, seaborn (visualization)
- scikit-learn (statistics)

### Reproduce Main Results

```bash
# Run complete analysis pipeline
python code/run_analysis.py

# Generate all figures
python code/generate_figures.py

# Run validation tests
python code/run_validations.py
```

---

## Data

### Source Data

Raw EEG data from the **PhysioNet EEG Motor Movement/Imagery Dataset**:
- Dataset: https://physionet.org/content/eegmmidb/1.0.0/
- 64-channel EEG, 160 Hz sampling rate
- Conditions: Eyes-closed rest (R02), Eyes-open rest (R01), Motor imagery (R04)

**Note:** Raw EEG files are not included in this repository due to size. Download from PhysioNet link above.

### Processed Data

This repository includes processed data files in `data/processed/`:
- Connectivity matrices (Pearson, PLV, Coherence)
- Graph Laplacian eigenvalues
- Rescaled spectral profiles
- Band-averaged correlations
- Statistical test results

All data files are in CSV format for easy access.

---

## Main Results

### Spectral Universality

**Eyes-closed resting state:**
- Overall correlation: r = 0.9852 (95% CI [0.980, 0.990])
- Band 1: r = 0.9935
- Band 2: r = 0.9941
- Band 3: r = 0.9932
- Band 4: r = 0.9967 (99.67% variance explained!)
- Band 5: r = 0.9485

**Null model comparison:**
- Observed: r = 0.9852
- Null expectation: r = 0.0024
- 410-fold greater than chance (p < 0.000001)

### Validation Results

All results survive rigorous validation:
- ✓ Bonferroni correction (α = 0.01, all p < 0.000001)
- ✓ Eyes-open control (r = 0.9555, only 3% lower)
- ✓ Rescaling independence (all 6 methods: r = 0.9852)
- ✓ Connectivity method robustness (PLV: 0.9974, Pearson: 0.9902, Coherence: 0.8538)

---

## Citation

If you use this code or data, please cite:

```bibtex
@article{Schorr2026spectral,
  title={Spectral Universality in Resting-State Brain Networks: Evidence for Equilibrium Dynamics},
  author={Schorr, Richard L.},
  journal={bioRxiv},
  year={2026},
  doi={YOUR_DOI_HERE}
}
```

---

## Figures

### Main Figures

**Figure 1:** λ₂ Universality in Resting-State Brain Networks  
**Figure 2:** Spectral Band Collapse After λ₂ Rescaling  
**Figure 3:** Validation Across Brain States and Task Conditions  
**Figure 4:** Topology Independence of Spectral Universality

### Supplementary Figures

**Figure S1:** Null Model Detailed Analysis  
**Figure S2:** Band Sensitivity Extended Analysis  
**Figure S3:** Eyes-Open vs Eyes-Closed Comparison  
**Figure S4:** Rescaling Parameter Comparison  
**Figure S5:** Connectivity Methods Comparison

All figures available in `figures/` directory in both PNG and PDF formats.

---

## Theoretical Framework

This work applies the **Phase-Modulated Information Rivalry (PMIR)** framework to neuroscience, demonstrating that resting brain networks exist in a universal equilibrium state characterized by spectral organization.

For PMIR theory and applications to other domains (cosmology, N-body dynamics, etc.), see:
- General PMIR framework: [link to main repo if available]
- Related publications: [Zenodo links]

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact

**Richard L. Schorr III**  
Independent Researcher  
Lancaster, Ohio, USA

Questions or collaboration inquiries: [Add email or create GitHub issues]

---

## Acknowledgments

- PhysioNet for providing the EEG Motor Movement/Imagery Dataset
- Schalk et al. (2004) for the BCI2000 system and data collection
- Open-source neuroscience community

---

## Related Publications

**Preprint:**  
Schorr, R. L. (2026). Spectral Universality in Resting-State Brain Networks: Evidence for Equilibrium Dynamics. *bioRxiv*. https://doi.org/YOUR_DOI_HERE

**Status:** Under review at PLOS Computational Biology

---

## Version History

- **v1.2** (Feb 2026): bioRxiv preprint with comprehensive validation
  - Added Bonferroni correction
  - Added eyes-open control analysis
  - Added rescaling parameter validation
  - Added connectivity method comparison

---

**Last updated:** February 2026
