# Brain Spectral Universality — PMIR Research Repository

A collection of papers demonstrating spectral universality in brain networks through the PMIR (Phase-Modulated Information Rivalry) framework.

## Papers

### Paper 01 — Spectral Universality in Resting-State Brain Networks: Evidence for Equilibrium Dynamics
`paper01_eeg/`

EEG-based analysis of 10 subjects (PhysioNet Motor Imagery dataset) demonstrating spectral universality via λ₂ rescaling. Submitted to bioRxiv; under appeal after initial screening error.

- **Key result:** r = 0.9852 spectral universality across resting-state conditions
- **Data:** PhysioNet EEG Motor Imagery (30 EDF files, 10 subjects × 3 runs)
- **Method:** Graph Laplacian spectral analysis with λ₂ rescaling

### Paper 02 — Universal Spectral Architecture of Resting-State Brain Networks
`paper02_abide/`

Multi-site fMRI validation across all 17 ABIDE neuroimaging sites. Demonstrates topology-independence of λ₂-rescaled spectral structure.

- **Key result:** 17/17 sites exceed r > 0.95 threshold (grand mean 0.9851)
- **Data:** ABIDE fMRI dataset, 17 acquisition sites
- **Method:** Connectivity method comparison, rescaling parameter sensitivity analysis

## Folder Structure

Each paper follows a consistent layout:
```
paperXX_name/
├── manuscript/   — PDF and source document files
├── code/         — Analysis scripts
├── data/         — Raw data and processed results
├── figures/      — Publication figures (main + supplementary)
└── tables/       — Supplementary tables (Paper 01) / results (Paper 02)
```

## Adding Future Papers

Create a new folder following the `paperXX_name` convention:
```
paper03_name/
├── manuscript/
├── code/
├── data/
├── figures/
└── results/
```

## Related Resources
- PMIR Preprints: Zenodo DOIs 10.5281/zenodo.18210474 – 10.5281/zenodo.18653051
- Framework: Phase-Modulated Information Rivalry (PMIR)
