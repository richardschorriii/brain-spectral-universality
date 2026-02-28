# Data

## Structure

```
data/
└── processed/       # Processed results (CSVs — tracked by git)
    raw/ is NOT here — see below for download instructions
```

## Raw Data Sources

Raw files are not stored in this repository (too large for GitHub).

**PhysioNet EEG (Paper 1 primary dataset):**
```
https://physionet.org/content/eegmmidb/1.0.0/
```
64-channel EEG, 160 Hz, N=109 subjects (eyes-closed rest, eyes-open rest, motor imagery tasks).

**ABIDE fMRI (Paper 1 cross-site validation):**
Downloaded automatically by the pipeline on first run:
```python
from nilearn import datasets
abide = datasets.fetch_abide_pcp(data_dir="./data/abide/")
```
17 acquisition sites, N=872 subjects.

**HCP Structural Connectomes (future papers):**
```
git clone https://github.com/Raj-Lab-UCSF/spectrome
```

## Adding data from future papers

Create subdirectories per paper:
```
data/processed/paper-02/
data/processed/paper-03/
```
Or use the corresponding paper branch. See `BRANCH_STRATEGY.md` in the root.
