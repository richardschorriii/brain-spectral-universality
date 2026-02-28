# PMIR Neuroscience Branch Strategy

This repository hosts the PMIR neuroscience paper series. Each paper gets its own branch,
branched from `main`, so every submission state is independently linkable and clean.

---

## Current Series

| Branch | Paper | Dataset | Status |
|--------|-------|---------|--------|
| `main` | **Paper 1:** Spectral universality in resting-state EEG | PhysioNet EEG, N=10 | Under review (bioRxiv appeal) |
| `paper-02` | **Paper 2:** ABIDE 17-site cross-site validation | ABIDE fMRI, N=872, 17 sites | In preparation |

---

## What Lives Where

### `main` — Paper 1 only
The canonical, frozen state of the original submission. **Do not add Paper 2 content here.**

```
code/                       ← shared analysis modules (data_acquisition, spectral_analysis, etc.)
data/processed/             ← Paper 1 data (spectral_properties, band_correlations, summary_results)
figures/main/               ← Paper 1 Figures 1–4 (λ₂ universality, band collapse, validation, topology)
figures/supplementary/      ← Paper 1 Figures S1–S5
tables/supplementary/       ← Paper 1 Tables S1–S4
manuscript/                 ← Paper 1 manuscripts only (BIORXIV-2026-707267v1, v1.2)
```

### `paper-02` — Paper 2 (ABIDE cross-validation)
Branched from `main`. Inherits all Paper 1 code and data, then adds Paper 2 material.

```
code/                       ← inherited from main + run_test_c_all_sites.py
data/processed/             ← Paper 1 data + test_c_all_sites.csv (17-site results)
figures/main/               ← Paper 1 figs + Figure4_ABIDE_AllSites_Updated.pdf/.png
figures/supplementary/      ← Paper 1 figs + any Paper 2 supplementary
manuscript/                 ← Paper 1 manuscripts + Brain_Spectral_Universality_Manuscript_v2.1.*
```

---

## How to Add a New Paper

### Step 1 — Create branch from main

```bash
git checkout main
git pull
git checkout -b paper-03
git push -u origin paper-03
```

Always branch from `main` (not from another paper branch), unless the new paper
directly extends the previous one's data (as paper-02 extends paper-01).

### Step 2 — Add paper-specific files

Paper-specific files go directly into the relevant folders on the new branch.
The branch itself IS the paper context — no subdirectory nesting needed.

```
data/processed/             ← add this paper's CSVs
figures/main/               ← add this paper's Figures 1–N
figures/supplementary/      ← add this paper's supplementary figures
tables/supplementary/       ← add this paper's tables
manuscript/                 ← add this paper's manuscript files
```

### Step 3 — Update README on the new branch

Add a paper-specific header block at the very top of README.md on the new branch:

```markdown
# Paper 3 — [Full Title]

**Branch:** `paper-03`  
**Preprint:** [DOI when available]  
**Datasets:** [list datasets]  
**Status:** [In preparation / Under review / Published]

> Paper 1 (EEG universality) is on `main`. Paper 2 (ABIDE) is on `paper-02`.

---
[rest of README continues below...]
```

### Step 4 — Commit and push

```bash
git add .
git commit -m "paper-03: initial state — [brief description]"
git push
```

### Step 5 — Tag submission snapshots

```bash
# When submitting to journal/preprint:
git tag paper-03-submitted-2026-09
git push origin paper-03-submitted-2026-09

# When accepted:
git tag paper-03-accepted-2026-12
git push origin paper-03-accepted-2026-12
```

---

## Planned Future Papers

| Branch | Topic | Priority |
|--------|-------|----------|
| `paper-03` | Consciousness-state gradient — wake→NREM spectral degradation (HCP + OpenNeuro) | High |
| `paper-04` | Mathematical physics bridge — spherical Laplacian to connectome eigenstructure | High |
| `paper-05` | Musical consonance as Laplacian attractor dynamics | Medium |
| `paper-06` | Grand cross-domain unification (PMIR across 12 orders of magnitude) | Long-term |

---

## Linking to Specific Paper States

For data availability statements in journal submissions:

```
# Link to a branch (living, may update):
https://github.com/richardschorriii/brain-spectral-universality/tree/paper-02

# Link to a frozen snapshot tag (preferred for peer review):
https://github.com/richardschorriii/brain-spectral-universality/tree/paper-02-submitted-2026-03
```

---

## Quick Reference

```bash
# See all branches
git branch -a

# See all tags
git tag -l

# Switch to paper-02 work
git checkout paper-02

# Return to main
git checkout main

# See what paper-02 adds on top of main
git diff main..paper-02 --stat
```
