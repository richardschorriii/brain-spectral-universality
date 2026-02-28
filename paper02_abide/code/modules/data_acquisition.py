"""
MODULE 1: Data Acquisition
Handles loading for all datasets. Returns standardized dicts.

Return format (every loader):
    {
        "subject_id": str,
        "adjacency_matrix": np.ndarray (N x N, non-negative, symmetric),
        "parcellation": str,
        "connectivity_method": str,
        "state": str,
        "dataset": str,
        "metadata": dict
    }
"""

import os
import numpy as np
import warnings
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# RAJ LAB HCP
# ─────────────────────────────────────────────────────────────────────────────

def load_raj_lab_hcp(data_path, parcellation="desikan", verbose=True):
    data_path = Path(data_path)
    subjects = []
    csv_file = data_path / "mean80_fibercount.csv"
    if csv_file.exists():
        try:
            mat = np.genfromtxt(str(csv_file), delimiter=",", skip_header=1)
            if mat.shape[0] != mat.shape[1]:
                mat = mat[:, 1:]
            mat = mat.astype(float)
            mat = np.abs(mat)
            mat = (mat + mat.T) / 2.0
            np.fill_diagonal(mat, 0)
            if verbose:
                print(f"[RAJ LAB] Loaded mean connectome shape: {mat.shape}")
            subjects.append({
                "subject_id": "hcp_mean80",
                "adjacency_matrix": mat,
                "parcellation": parcellation,
                "connectivity_method": "structural_dti",
                "state": "rest",
                "dataset": "raj_lab_hcp",
                "metadata": {"note": "group mean 80-subject HCP connectome"}
            })
        except Exception as e:
            warnings.warn(f"[RAJ LAB] Failed to load mean80_fibercount.csv: {e}")
    else:
        print(f"[RAJ LAB] No data found at {data_path}")
    if verbose:
        print(f"[RAJ LAB] Loaded {len(subjects)} subjects (mean connectome only)")
    return subjects


# ─────────────────────────────────────────────────────────────────────────────
# ABIDE
# ─────────────────────────────────────────────────────────────────────────────

def load_abide(data_path, max_subjects=None, verbose=True):
    """
    Load ABIDE from downloaded .1D files (bypasses nilearn).
    Reads site and diagnosis from phenotypic CSV.

    Phenotypic CSV columns used:
      SUB_ID    -> subject numeric ID
      DX_GROUP  -> 1=autism, 2=control
      SITE_ID   -> acquisition site (e.g. "NYU", "Pitt", "USM")
    """
    data_path = Path(data_path)
    abide_dir = data_path / "ABIDE_pcp" / "cpac" / "filt_noglobal"

    if not abide_dir.exists():
        print(f"[ABIDE] Data not found at {abide_dir}")
        print("[ABIDE] To download, run Python and execute:")
        print("  from nilearn import datasets")
        print(f"  datasets.fetch_abide_pcp(data_dir=r'{data_path}', pipeline='cpac',")
        print("    band_pass_filtering=True, global_signal_regression=False,")
        print("    derivatives=['rois_cc200'], verbose=1)")
        return []

    roi_files = sorted(abide_dir.glob("*_rois_cc200.1D"))
    if not roi_files:
        print(f"[ABIDE] No *_rois_cc200.1D files found in {abide_dir}")
        return []

    if verbose:
        print(f"[ABIDE] Found {len(roi_files)} .1D files, loading...")

    if max_subjects is not None:
        roi_files = roi_files[:max_subjects]

    # Build pheno dict keyed by numeric subject ID (no leading zeros)
    # pheno[str_id] = {"dx": int_or_None, "site": str}
    pheno = {}
    pheno_file = data_path / "ABIDE_pcp" / "Phenotypic_V1_0b_preprocessed1.csv"
    if pheno_file.exists():
        try:
            import pandas as pd
            df = pd.read_csv(str(pheno_file))
            for _, row in df.iterrows():
                try:
                    sid = str(int(float(row.get("SUB_ID", 0))))
                except (ValueError, TypeError):
                    continue
                dx   = row.get("DX_GROUP", None)
                site = str(row.get("SITE_ID", "unknown"))
                pheno[sid] = {"dx": int(dx) if dx and not np.isnan(float(dx)) else None,
                               "site": site}
        except Exception as e:
            warnings.warn(f"[ABIDE] pheno CSV parse failed: {e}")
    else:
        warnings.warn(f"[ABIDE] Phenotypic CSV not found at {pheno_file}")

    subjects = []
    failed = 0

    for f in roi_files:
        try:
            # Filename examples:
            #   "Pitt_0050003_rois_cc200.1D"  -> site=Pitt, num=50003
            #   "0050142_rois_cc200.1D"       -> site from pheno only
            stem  = f.stem.replace("_rois_cc200", "")
            parts = stem.split("_")

            # Last digit-only part = subject number
            subj_num_raw = next((p for p in reversed(parts) if p.isdigit()), None)
            # Strip leading zeros for pheno key
            subj_num_key = str(int(subj_num_raw)) if subj_num_raw else None

            # First non-digit part = site from filename (may be absent)
            site_from_name = next((p for p in parts if not p.isdigit()), None)

            # Full stem as subject_id (preserves site prefix when present)
            subj_id = stem

            # Load time series
            ts = np.loadtxt(str(f))
            if ts.ndim != 2 or ts.shape[0] < 10 or ts.shape[1] < 2:
                failed += 1
                continue

            # Correlation matrix
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                corr = np.corrcoef(ts.T)
            corr = np.nan_to_num(corr, nan=0.0)
            corr = np.abs(corr)
            np.fill_diagonal(corr, 0)

            # Pheno lookup
            pheno_entry = pheno.get(subj_num_key, {})
            dx          = pheno_entry.get("dx")
            site_pheno  = pheno_entry.get("site", "unknown")

            # Site: prefer filename prefix (reliable), fall back to pheno CSV
            final_site = site_from_name if site_from_name else site_pheno

            subjects.append({
                "subject_id": subj_id,
                "adjacency_matrix": corr,
                "parcellation": "cc200",
                "connectivity_method": "pearson",
                "state": "rest",
                "dataset": "abide",
                "metadata": {
                    "diagnosis": dx,        # 1=autism, 2=control
                    "dx_group":  dx,
                    "site":      final_site,
                    "subject_num": subj_num_key,
                    "source_file": f.name,
                }
            })

        except Exception as e:
            failed += 1
            if verbose:
                warnings.warn(f"[ABIDE] {f.name}: {e}")

    if verbose:
        # Report site breakdown
        site_counts = {}
        for s in subjects:
            st = s["metadata"]["site"]
            site_counts[st] = site_counts.get(st, 0) + 1
        dx_counts = {1: 0, 2: 0, None: 0}
        for s in subjects:
            dx_counts[s["metadata"]["diagnosis"]] = \
                dx_counts.get(s["metadata"]["diagnosis"], 0) + 1

        print(f"[ABIDE] Loaded {len(subjects)} subjects ({failed} failed)")
        print(f"[ABIDE] Sites: {dict(sorted(site_counts.items(), key=lambda x: -x[1]))}")
        print(f"[ABIDE] DX: ASD={dx_counts.get(1,0)}, Control={dx_counts.get(2,0)}, "
              f"Unknown={dx_counts.get(None,0)}")

    return subjects


# ─────────────────────────────────────────────────────────────────────────────
# OPENNEURO
# ─────────────────────────────────────────────────────────────────────────────

def load_openneuro_dataset(dataset_id, data_path, states=None, verbose=True):
    data_path = Path(data_path)
    if not data_path.exists():
        print(f"[OpenNeuro {dataset_id}] Data not found at {data_path}")
        return []

    subjects = []
    bold_files = sorted(list(data_path.glob("sub-*/func/*_bold.nii.gz")) +
                        list(data_path.glob("sub-*/func/*_bold.nii")))
    if verbose:
        print(f"[OpenNeuro {dataset_id}] Found {len(bold_files)} BOLD files")

    for bold_file in bold_files:
        try:
            fname = bold_file.name
            sub_id = _parse_bids_entity(fname, "sub")
            task   = _parse_bids_entity(fname, "task")
            state  = _map_task_to_state(task, dataset_id)
            if states is not None and state not in states:
                continue
            ts = _extract_bold_timeseries(bold_file)
            if ts is None:
                continue
            corr = np.corrcoef(ts.T)
            corr = np.nan_to_num(corr, nan=0.0)
            corr = np.abs(corr)
            np.fill_diagonal(corr, 0)
            subjects.append({
                "subject_id": sub_id,
                "adjacency_matrix": corr,
                "parcellation": "schaefer100",
                "connectivity_method": "pearson",
                "state": state,
                "dataset": dataset_id,
                "metadata": {"bold_file": str(bold_file), "task": task}
            })
        except Exception as e:
            warnings.warn(f"[OpenNeuro {dataset_id}] Failed {bold_file.name}: {e}")

    if verbose:
        print(f"[OpenNeuro {dataset_id}] Loaded {len(subjects)} subject-state pairs")
    return subjects


def _extract_bold_timeseries(bold_file):
    try:
        from nilearn import datasets as nl_datasets
        from nilearn.maskers import NiftiLabelsMasker
        schaefer = nl_datasets.fetch_atlas_schaefer_2018(n_rois=100)
        masker   = NiftiLabelsMasker(labels_img=schaefer.maps, standardize=True,
                                     memory="nilearn_cache", verbose=0)
        return masker.fit_transform(str(bold_file))
    except Exception as e:
        warnings.warn(f"Time series extraction failed: {e}")
        return None


def _parse_bids_entity(filename, entity):
    import re
    m = re.search(rf"{entity}-([a-zA-Z0-9]+)", filename)
    return m.group(1) if m else "unknown"


def _map_task_to_state(task, dataset_id):
    mappings = {
        "ds003768": {"rest": "wake", "NREM1": "NREM1", "NREM2": "NREM2",
                     "NREM3": "NREM3", "nrem1": "NREM1", "nrem2": "NREM2",
                     "nrem3": "NREM3", "sleep": "NREM2"},
        "propofol": {"rest": "awake", "imagery": "awake",
                     "propofollow": "light_sedation", "propofolhigh": "deep_sedation"},
    }
    return mappings.get(dataset_id, {}).get(task, task)


# ─────────────────────────────────────────────────────────────────────────────
# MASTER LOADER
# ─────────────────────────────────────────────────────────────────────────────

def load_all_datasets(config):
    all_subjects = []
    for name, cfg in config.DATASETS.items():
        if not cfg.get("enabled", True):
            print(f"[LOADER] Skipping {name} (disabled)")
            continue
        print(f"\n[LOADER] Loading: {name}")
        if name == "raj_lab_hcp":
            subs = load_raj_lab_hcp(cfg["data_path"])
        elif name == "abide":
            subs = load_abide(cfg["data_path"], max_subjects=cfg.get("max_subjects"))
        elif name in ("openneuro_sleep", "openneuro_propofol"):
            subs = load_openneuro_dataset(
                dataset_id=cfg.get("dataset_id", name),
                data_path=cfg["data_path"],
                states=cfg.get("states"))
        else:
            print(f"[LOADER] Unknown dataset {name}, skipping")
            subs = []
        all_subjects.extend(subs)
        print(f"[LOADER] {name}: {len(subs)} subjects")
    print(f"\n[LOADER] Total: {len(all_subjects)} subjects")
    return all_subjects
