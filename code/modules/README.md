# Core Analysis Modules — Paper 1

These modules implement the full spectral universality pipeline.

## Current Contents

| File | Status | Description |
|------|--------|-------------|
| `config.py` | ⚠️ duplicate | Same as `../config.py` — use the parent copy |
| `download_abide.py` | ✓ present | ABIDE data download helper |
| `run_pipeline.py` | ⚠️ duplicate | Same as `../run_pipeline.py` — use the parent copy |
| `run_refined_tests.py` | ⚠️ duplicate | Same as `../run_refined_tests.py` — use parent copy |
| `run_test_c_all_sites.py` | ⚠️ duplicate | Same as `../run_test_c_all_sites.py` — use parent copy |

**Note:** The runner scripts (run_*.py, config.py) should live in `code/` not here.
The duplicate copies in this folder can be deleted once confirmed they match the parent.

## Module Files (to be added)

These four modules contain the core scientific logic documented in code/README.md:

| File | Description |
|------|-------------|
| `data_acquisition.py` | Dataset loading — ABIDE, HCP, OpenNeuro (BIDS) |
| `spectral_analysis.py` | Laplacian construction, eigendecomposition, λ₂ rescaling |
| `null_models.py` | Erdős-Rényi, degree-preserved, strength-preserved null models |
| `consciousness_analysis.py` | State-ordered universality gradient, parcellation robustness |

See `../README.md` for full function signatures and usage examples.
