# Analysis Code

Python scripts to reproduce all analyses from Schorr (2026).

## Structure

```
code/
├── config.py                   # All parameters — edit this first
├── run_pipeline.py             # Master pipeline orchestrator
└── modules/
    ├── data_acquisition.py     # Dataset loading (ABIDE, HCP, OpenNeuro)
    ├── spectral_analysis.py    # Laplacian, eigendecomposition, λ₂ rescaling
    ├── null_models.py          # Configuration model + permutation tests
    └── consciousness_analysis.py  # State gradient + parcellation independence
```

## Quick Start

```bash
# 1. Edit config.py to set data paths and toggle datasets
# 2. Follow download instructions printed by stage_0_setup()
python code/run_pipeline.py

# Or run just the spectral analysis on your own connectivity matrix:
from code.modules.spectral_analysis import (
    build_laplacian, compute_eigenspectrum, rescale_spectrum
)
import numpy as np

A = your_adjacency_matrix  # N x N, symmetric, non-negative
L = build_laplacian(A)
eigenvalues = compute_eigenspectrum(L)
rescaled = rescale_spectrum(eigenvalues, method="lambda2")
```

## Key Functions

### `spectral_analysis.py`
- `build_laplacian(A)` — Combinatorial Laplacian L = D - A
- `compute_eigenspectrum(L)` — Full eigendecomposition, sorted ascending
- `get_lambda2(eigenvalues)` — Extract algebraic connectivity (Fiedler value)
- `rescale_spectrum(eigenvalues, method="lambda2")` — PMIR rescaling
- `compute_pairwise_correlations(spectra_list)` — Inter-subject correlation matrix
- `compute_spectral_universality(subjects, ...)` — Full pipeline on subject list
- `compare_rescaling_methods(subjects, methods)` — λ₂ vs alternatives

### `null_models.py`
- `generate_erdos_renyi(A)` — Random graph matching edge density
- `generate_degree_preserved(A)` — Maslov-Sneppen edge rewiring
- `generate_strength_preserved(A)` — Chung-Lu weighted null model
- `run_all_null_models(subjects, observed_r, ...)` — Batch null evaluation
- `permutation_test(spectra_list, n_permutations=10000)` — Label shuffling

### `data_acquisition.py`
- `load_abide(data_path)` — Via nilearn auto-download
- `load_raj_lab_hcp(data_path)` — Structural connectomes from spectrome repo
- `load_openneuro_dataset(dataset_id, data_path)` — Generic BIDS loader
- `load_all_datasets(config)` — Load everything enabled in config.py

### `consciousness_analysis.py`
- `analyze_consciousness_gradient(subjects)` — State-ordered universality
- `test_parcellation_independence(subjects_by_parcellation)` — Atlas robustness
- `quantify_universality_drop(gradient_test)` — Δr from wake to deepest state

## Dependencies

```bash
pip install numpy scipy pandas matplotlib seaborn nilearn scikit-learn mne
```

See `../requirements.txt` for pinned versions.

## Data Download

Follow instructions printed by `python code/run_pipeline.py` (stage 0).
Key datasets:
- **ABIDE**: Auto-downloaded via nilearn on first run (~2GB)
- **HCP**: `git clone https://github.com/Raj-Lab-UCSF/spectrome`
- **OpenNeuro ds003768**: `aws s3 sync s3://openneuro.org/ds003768 <path> --no-sign-request`
