"""
MODULE 2: Spectral Analysis
Core computations:
  1. Graph Laplacian: L = D - A
  2. Full eigenspectrum via scipy
  3. λ₂ rescaling: λ̃_k = λ_k / λ₂
  4. Inter-subject correlation of rescaled spectra
  5. All alternative rescaling methods (for comparison)

PMIR prediction: ρ(λ/λ₂) is universal across subjects and consciousness states.
Falsification tests live in null_models.py.
"""

import numpy as np
import warnings
import os
import pickle
from pathlib import Path
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigsh
from scipy.linalg import eigh  # for dense matrices


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: BUILD GRAPH LAPLACIAN
# L = D - A   (combinatorial Laplacian, as specified in research plan)
# ─────────────────────────────────────────────────────────────────────────────

def build_laplacian(adjacency_matrix, laplacian_type="combinatorial", verify=True):
    """
    Compute graph Laplacian from weighted adjacency matrix.

    adjacency_matrix: N×N numpy array, non-negative, symmetric
    laplacian_type:
        "combinatorial"  — L = D - A                    (research plan default)
        "normalized"     — L_sym = D^-1/2 L D^-1/2      (alternative)
        "random_walk"    — L_rw = D^-1 L                 (alternative)

    Returns: L (N×N numpy array)
    """
    A = adjacency_matrix.copy().astype(float)

    # Enforce symmetry and non-negativity
    A = (A + A.T) / 2.0
    A = np.maximum(A, 0)
    np.fill_diagonal(A, 0)

    if verify:
        assert np.allclose(A, A.T, atol=1e-10), "Adjacency matrix not symmetric"
        assert np.all(A >= 0), "Negative weights found"

    # Degree matrix
    degrees = A.sum(axis=1)
    D = np.diag(degrees)

    if laplacian_type == "combinatorial":
        L = D - A

    elif laplacian_type == "normalized":
        # L_sym = D^-1/2 (D - A) D^-1/2 = I - D^-1/2 A D^-1/2
        d_inv_sqrt = np.where(degrees > 0, 1.0 / np.sqrt(degrees), 0.0)
        D_inv_sqrt = np.diag(d_inv_sqrt)
        L_comb = D - A
        L = D_inv_sqrt @ L_comb @ D_inv_sqrt

    elif laplacian_type == "random_walk":
        d_inv = np.where(degrees > 0, 1.0 / degrees, 0.0)
        D_inv = np.diag(d_inv)
        L_comb = D - A
        L = D_inv @ L_comb

    else:
        raise ValueError(f"Unknown laplacian_type: {laplacian_type}")

    return L


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: COMPUTE EIGENSPECTRUM
# λ₁ = 0 (always for connected graph Laplacian)
# λ₂ = algebraic connectivity (Fiedler value)
# Full spectrum λ₁ ≤ λ₂ ≤ ... ≤ λ_N
# ─────────────────────────────────────────────────────────────────────────────

def compute_eigenspectrum(L, method="full", n_eigenvalues=None, verify=True):
    """
    Compute eigenspectrum of graph Laplacian.

    method:
        "full"   — scipy.linalg.eigh (exact, all eigenvalues)
                   Use for parcellated connectomes (N ≤ 400 regions)
        "sparse" — scipy.sparse.linalg.eigsh (iterative, partial spectrum)
                   Use for very large matrices (N > 1000 regions)

    Returns: eigenvalues sorted ascending (λ₁=0, λ₂, ..., λ_N)
    """
    N = L.shape[0]

    if method == "full" or (n_eigenvalues is None or n_eigenvalues >= N):
        # Use dense solver — exact, returns all N eigenvalues
        eigenvalues = eigh(L, eigvals_only=True)
        eigenvalues = np.sort(eigenvalues)

    elif method == "sparse":
        k = min(n_eigenvalues, N - 1)
        L_sparse = csr_matrix(L)
        eigenvalues, _ = eigsh(L_sparse, k=k, which="SM")
        eigenvalues = np.sort(np.real(eigenvalues))

    else:
        raise ValueError(f"Unknown method: {method}")

    # Clip tiny negative values due to floating point (λ₁ should be exactly 0)
    eigenvalues = np.maximum(eigenvalues, 0)

    if verify:
        if eigenvalues[0] > 1e-6:
            warnings.warn(f"λ₁ = {eigenvalues[0]:.2e} (expected ≈ 0). Graph may be disconnected.")

    return eigenvalues


def get_lambda2(eigenvalues):
    """Extract λ₂ (algebraic connectivity / Fiedler value)."""
    # λ₁ = 0 is always index 0; λ₂ is the second smallest
    positive_eigs = eigenvalues[eigenvalues > 1e-10]
    if len(positive_eigs) == 0:
        raise ValueError("No positive eigenvalues found. Graph is fully disconnected?")
    return positive_eigs[0]


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: RESCALING
# PMIR prediction: λ̃_k = λ_k / λ₂ collapses spectra universally
# ─────────────────────────────────────────────────────────────────────────────

RESCALING_FUNCTIONS = {
    "lambda2": lambda eigs: eigs / get_lambda2(eigs),
    "lambda_max": lambda eigs: eigs / eigs[-1],
    "mean_eigenvalue": lambda eigs: eigs / np.mean(eigs[eigs > 1e-10]),
    "spectral_radius": lambda eigs: eigs / eigs[-1],  # same as lambda_max for Laplacian
}

def rescale_spectrum(eigenvalues, method="lambda2"):
    """
    Rescale eigenspectrum by the specified method.

    Returns: rescaled eigenvalues (same length as input)
    """
    if method not in RESCALING_FUNCTIONS:
        raise ValueError(f"Unknown rescaling method: {method}. "
                         f"Options: {list(RESCALING_FUNCTIONS.keys())}")
    return RESCALING_FUNCTIONS[method](eigenvalues.copy())


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: INTER-SUBJECT CORRELATION
# Core test of universality: how similar are rescaled spectra across subjects?
# ─────────────────────────────────────────────────────────────────────────────

def compute_collapse_score(rescaled_spectra_list, interpolate_to=None, n_quantile_points=200):
    """
    Collapse quality score: how tightly do rescaled spectra cluster in shape?

    THE KEY INSIGHT:
    After lambda2 rescaling, spectra span different x-axis ranges because
    lambda_max/lambda2 varies across subjects. Comparing by index position
    (spectrum[k] vs spectrum[k]) mixes up different spectral locations.

    CORRECT APPROACH: evaluate each spectrum at common QUANTILE positions.
    Map each subject's spectrum to percentile ranks [0,1], then compare the
    eigenvalue at the same percentile across subjects. This isolates shape
    universality from scale differences.

    Metric: mean pointwise CV across quantile positions. LOWER = better shape collapse.

    Band scores split the quantile axis into 5 equal bands.
    """
    n = len(rescaled_spectra_list)
    quantile_grid = np.linspace(0.0, 1.0, n_quantile_points)

    # For each subject: evaluate spectrum at common quantile positions
    # using linear interpolation of the empirical quantile function
    shape_curves = []
    for eigs in rescaled_spectra_list:
        eigs_sorted = np.sort(eigs)  # already sorted, but ensure
        # Drop the zero eigenvalue (lambda1=0) which is structurally fixed
        eigs_pos = eigs_sorted[eigs_sorted > 1e-10]
        if len(eigs_pos) < 2:
            continue
        # Empirical quantile positions for this subject's positive eigenvalues
        q_positions = np.linspace(0.0, 1.0, len(eigs_pos))
        # Interpolate to common grid
        shape_curve = np.interp(quantile_grid, q_positions, eigs_pos)
        shape_curves.append(shape_curve)

    if len(shape_curves) < 2:
        warnings.warn("Too few valid spectra for collapse score")
        return {"collapse_score": np.nan, "mean_rmsd": np.nan,
                "mean_curve": None, "std_curve": None,
                "band_scores": {}, "n_subjects": n, "spectra_matrix": None}

    S = np.array(shape_curves)  # (n_subjects, n_quantile_points)

    # Normalize each row to [0,1] so we compare shape, not scale
    # This is the key step: after this, CV measures shape deviation only
    row_min = S.min(axis=1, keepdims=True)
    row_max = S.max(axis=1, keepdims=True)
    with np.errstate(invalid='ignore', divide='ignore'):
        S_norm = np.where(row_max > row_min, (S - row_min) / (row_max - row_min), 0.0)

    mean_curve = S_norm.mean(axis=0)
    std_curve  = S_norm.std(axis=0)

    # CV on normalized shape curves
    with np.errstate(invalid='ignore', divide='ignore'):
        cv = np.where(mean_curve > 1e-6, std_curve / mean_curve, std_curve)

    collapse_score = float(cv.mean())

    # RMSD from mean shape curve
    rmsd_per_subject = np.sqrt(((S_norm - mean_curve) ** 2).mean(axis=1))
    mean_rmsd = float(rmsd_per_subject.mean())

    # Band-wise scores (5 equal bands over quantile axis)
    band_scores = {}
    for band_idx in range(5):
        lo = band_idx * n_quantile_points // 5
        hi = (band_idx + 1) * n_quantile_points // 5
        band_scores[band_idx + 1] = float(cv[lo:hi].mean())

    return {
        "collapse_score": collapse_score,
        "mean_rmsd": mean_rmsd,
        "mean_curve": mean_curve,
        "std_curve": std_curve,
        "band_scores": band_scores,
        "n_subjects": len(shape_curves),
        "spectra_matrix": S_norm,
    }


def compute_pairwise_correlations(rescaled_spectra_list, interpolate_to=None):
    """
    Compute all pairwise Pearson correlations between rescaled spectra.

    rescaled_spectra_list: list of 1D numpy arrays (rescaled eigenvalues)
    interpolate_to: if int, interpolate all spectra to this common length
                    (needed when subjects have different N due to parcellation)

    Returns:
        correlation_matrix: (n_subjects × n_subjects) numpy array
        mean_correlation: float (average of off-diagonal elements)
    """
    n = len(rescaled_spectra_list)

    # Interpolate to common length if needed
    if interpolate_to is not None:
        spectra = [_interpolate_spectrum(s, interpolate_to)
                   for s in rescaled_spectra_list]
    else:
        # Verify all same length
        lengths = [len(s) for s in rescaled_spectra_list]
        if len(set(lengths)) > 1:
            interpolate_to = min(lengths)
            warnings.warn(f"Spectra have different lengths {set(lengths)}. "
                          f"Interpolating to {interpolate_to}.")
            spectra = [_interpolate_spectrum(s, interpolate_to)
                       for s in rescaled_spectra_list]
        else:
            spectra = rescaled_spectra_list

    # Stack into matrix (n_subjects × n_points)
    S = np.array(spectra)

    # Pearson correlation matrix
    # np.corrcoef computes correlations along rows
    corr_matrix = np.corrcoef(S)

    # Extract off-diagonal elements (pairwise subject correlations)
    mask = ~np.eye(n, dtype=bool)
    off_diagonal = corr_matrix[mask]
    mean_corr = np.mean(off_diagonal)

    return corr_matrix, mean_corr


def _interpolate_spectrum(eigenvalues, target_length):
    """Interpolate eigenvalue spectrum to a target length."""
    from scipy.interpolate import interp1d
    x_old = np.linspace(0, 1, len(eigenvalues))
    x_new = np.linspace(0, 1, target_length)
    f = interp1d(x_old, eigenvalues, kind="linear")
    return f(x_new)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: FULL PIPELINE FOR A SUBJECT LIST
# ─────────────────────────────────────────────────────────────────────────────

def compute_spectral_universality(subjects, rescaling_method="lambda2",
                                   laplacian_type="combinatorial",
                                   cache_dir=None, verbose=True):
    """
    Run the full spectral universality pipeline on a list of subject dicts.

    For each subject:
      1. Build Laplacian
      2. Compute eigenspectrum
      3. Rescale by specified method
      4. Collect rescaled spectra

    Then compute pairwise inter-subject correlations.

    Returns dict with:
        - eigenspectra: list of raw eigenvalues per subject
        - rescaled_spectra: list of rescaled eigenvalues per subject
        - correlation_matrix: N_sub × N_sub correlation matrix
        - mean_correlation: float
        - lambda2_values: list of λ₂ per subject (informative)
        - subject_ids: list of subject IDs
        - rescaling_method: str
    """
    eigenspectra = []
    rescaled_spectra = []
    lambda2_values = []
    subject_ids = []

    for i, sub in enumerate(subjects):
        sub_id = sub["subject_id"]
        if verbose and i % 50 == 0:
            print(f"  [{rescaling_method}] Processing subject {i+1}/{len(subjects)}: {sub_id}")

        # Cache check
        cache_key = f"{sub_id}_{laplacian_type}"
        cached = _load_from_cache(cache_dir, cache_key)

        if cached is not None:
            eigs = cached
        else:
            try:
                L = build_laplacian(sub["adjacency_matrix"], laplacian_type)
                eigs = compute_eigenspectrum(L, method="full")
                _save_to_cache(cache_dir, cache_key, eigs)
            except Exception as e:
                warnings.warn(f"Failed subject {sub_id}: {e}")
                continue

        try:
            lam2 = get_lambda2(eigs)
            rescaled = rescale_spectrum(eigs, method=rescaling_method)

            eigenspectra.append(eigs)
            rescaled_spectra.append(rescaled)
            lambda2_values.append(lam2)
            subject_ids.append(sub_id)
        except Exception as e:
            warnings.warn(f"Rescaling failed for {sub_id}: {e}")

    if len(rescaled_spectra) == 0:
        warnings.warn("No spectra computed successfully")
        return None

    # Compute inter-subject correlations
    corr_matrix, mean_corr = compute_pairwise_correlations(rescaled_spectra)

    # Compute collapse score (the metric that actually distinguishes methods)
    collapse = compute_collapse_score(rescaled_spectra)

    if verbose:
        print(f"  [{rescaling_method}] Mean inter-subject correlation: r = {mean_corr:.4f}")
        print(f"  [{rescaling_method}] Collapse score (CV, lower=better): {collapse['collapse_score']:.4f}")
        print(f"  [{rescaling_method}] Mean RMSD from universal curve:     {collapse['mean_rmsd']:.4f}")
        print(f"  [{rescaling_method}] λ₂ range: [{min(lambda2_values):.4f}, {max(lambda2_values):.4f}]")
        print(f"  [{rescaling_method}] λ₂ CV: {np.std(lambda2_values)/np.mean(lambda2_values)*100:.1f}%")

    return {
        "eigenspectra": eigenspectra,
        "rescaled_spectra": rescaled_spectra,
        "correlation_matrix": corr_matrix,
        "mean_correlation": mean_corr,
        "collapse_score": collapse["collapse_score"],
        "mean_rmsd": collapse["mean_rmsd"],
        "collapse_details": collapse,
        "lambda2_values": np.array(lambda2_values),
        "subject_ids": subject_ids,
        "rescaling_method": rescaling_method,
        "laplacian_type": laplacian_type,
        "n_subjects": len(subject_ids),
    }


# ─────────────────────────────────────────────────────────────────────────────
# RESCALING COMPARISON — test all methods, check if λ₂ is privileged
# ─────────────────────────────────────────────────────────────────────────────

def compare_rescaling_methods(subjects, methods=None, laplacian_type="combinatorial",
                               cache_dir=None, verbose=True):
    """
    Run the pipeline for all rescaling methods and collect results.
    If any alternative matches λ₂ collapse quality, λ₂ claim is weakened.

    Returns dict: {method_name: result_dict}
    """
    if methods is None:
        methods = ["lambda2", "lambda_max", "mean_eigenvalue"]

    results = {}
    for method in methods:
        if verbose:
            print(f"\n[RESCALING COMPARISON] Testing method: {method}")
        results[method] = compute_spectral_universality(
            subjects, rescaling_method=method,
            laplacian_type=laplacian_type,
            cache_dir=cache_dir, verbose=verbose
        )

    # Summary — use collapse_score (not Pearson r) as the discriminating metric
    if verbose:
        print("\n[RESCALING COMPARISON] Summary:")
        print(f"NOTE: Pearson r cannot distinguish rescaling methods (scale-invariant).")
        print(f"      Using collapse score (mean CV) — LOWER is better collapse.")
        print(f"{'Method':<20} {'Mean r':<10} {'Collapse↓':<12} {'RMSD↓':<10} {'Result'}")
        print("-" * 68)
        lambda2_cs = results.get("lambda2", {}).get("collapse_score", np.nan)
        for method, res in results.items():
            if res is None:
                continue
            r   = res["mean_correlation"]
            cs  = res["collapse_score"]
            rmsd= res["mean_rmsd"]
            if method == "lambda2":
                status = "★ PMIR prediction"
            elif cs < lambda2_cs + 0.001:  # within noise of λ₂
                status = "⚠ TIES WITH λ₂"
            elif cs < lambda2_cs:
                status = "⚠ BETTER THAN λ₂"
            else:
                status = "✓ worse collapse"
            print(f"{method:<20} {r:<10.4f} {cs:<12.4f} {rmsd:<10.4f} {status}")

    return results


# ─────────────────────────────────────────────────────────────────────────────
# CACHE UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def _save_to_cache(cache_dir, key, data):
    if cache_dir is None:
        return
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, f"{key}.pkl")
    with open(path, "wb") as f:
        pickle.dump(data, f)


def _load_from_cache(cache_dir, key):
    if cache_dir is None:
        return None
    path = os.path.join(cache_dir, f"{key}.pkl")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None
