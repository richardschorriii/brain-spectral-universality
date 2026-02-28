# Processed Data — Paper 1

Results from the spectral universality analysis pipeline.
Dataset: PhysioNet EEG Motor Movement/Imagery, N=10 subjects (S001–S010).

## Files

| File | Description | Shape |
|------|-------------|-------|
| `spectral_properties.csv` | Per-subject λ₂ values in resting and task conditions | 20 rows × 3 cols |
| `band_correlations.csv` | Mean inter-subject correlation per frequency band × condition | 10 rows × 5 cols |
| `summary_results.csv` | Overall universality metrics (r, difference rest vs. task, n_subjects) | 1 row × 7 cols |

## Raw Data

Raw EEG files (.edf) are NOT stored here — too large for GitHub.
Download from: https://physionet.org/content/eegmmidb/1.0.0/

---

> **Paper 2 data** (ABIDE 17-site: `test_c_all_sites.csv`) is on the `paper-02` branch.
