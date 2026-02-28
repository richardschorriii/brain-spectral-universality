"""
MODULE: refined_tests.py  (v3 — redesigned to match data structure)

ROOT CAUSE ANALYSIS OF v1/v2 FAILURES:
========================================

Test B (landscape): fMRI correlation matrix spectra lie on a 1D manifold
(differ primarily by scale, not shape). Any rescaling parameter produces
identical CV because CV = std/mean is scale-invariant. The landscape test
cannot discriminate rescaling parameters on this data.

  REDESIGN: Eigenvalue Stability Analysis.
    For each rank k, compute CV(lambda_k) across subjects WITHOUT rescaling.
    Lambda2 should have distinctive stability properties that justify it as
    the natural reference eigenvalue. Also test: which eigenvalue, when used
    as reference, minimizes the RMSD from the mean rescaled curve (not CV).

Test A (decomposition): Within-subject r=0.90 shows degree sequence predicts
each subject's spectrum well. But cross-subject, all CL spectra collapse to
the same curve → R²=0. This is actually the correct result: universality is
enforced by the shared degree-constraint template, not subject-specific degrees.

  REDESIGN: Distinguish three variance components:
    1. Between-subject CL variance (near zero → universality IS degree-constrained)
    2. Within-subject residual (actual - CL) variance
    3. Test whether the within-subject residual (higher-order structure)
       correlates with diagnosis → validates PMIR's individuated component claim

Test C (replication): Synthetic Lausanne (34-59 region fragments) is
incompatible with real ABIDE (200 regions). Structural vs functional
spectra have different absolute scales and different shapes.

  REDESIGN: Internal replication using ABIDE site splits.
    Different acquisition sites = meaningful replication (different scanners,
    protocols, populations within same modality+atlas). Same as ABIDE II
    approach but uses existing data.

TESTS IN THIS FILE:
  A: Three-Component Variance Analysis
  B: Eigenvalue Stability + RMSD Landscape
  C: Site-Based Replication within ABIDE
"""

import numpy as np
import warnings
from scipy.linalg import eigh
from scipy.stats import pearsonr, spearmanr

from .spectral_analysis import (
    build_laplacian, compute_eigenspectrum, get_lambda2,
    compute_collapse_score, compute_spectral_universality,
    _load_from_cache, _save_to_cache
)


# ─────────────────────────────────────────────────────────────────────────────
# SHARED UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def _threshold_adjacency(A, target_density=0.15):
    """Threshold weighted matrix to target edge density for Chung-Lu."""
    A = A.copy()
    np.fill_diagonal(A, 0)
    N = A.shape[0]
    n_edges = int(target_density * N * (N - 1) / 2)
    upper = A[np.triu_indices(N, k=1)]
    if n_edges >= len(upper):
        return (A > 0).astype(float)
    threshold = np.sort(upper)[::-1][n_edges]
    A_bin = np.triu((A >= threshold).astype(float), 1)
    return A_bin + A_bin.T


def _to_shape_curve(eigs, q_grid):
    """Project eigenvalues to normalized [0,1] shape curve at quantile positions."""
    pos = eigs[eigs > 1e-10]
    if len(pos) < 2:
        return None
    q_pos = np.linspace(0, 1, len(pos))
    curve = np.interp(q_grid, q_pos, pos)
    cmin, cmax = curve.min(), curve.max()
    return (curve - cmin) / (cmax - cmin) if cmax > cmin else np.zeros_like(curve)


def _get_eigenspectra(subjects, cache_dir, verbose=False):
    """Load or compute combinatorial Laplacian eigenvalues for all subjects."""
    spectra = []
    for i, sub in enumerate(subjects):
        sub_id = sub["subject_id"]
        key = f"{sub_id}_combinatorial"
        eigs = _load_from_cache(cache_dir, key)
        if eigs is None:
            try:
                L = build_laplacian(sub["adjacency_matrix"], "combinatorial")
                eigs = compute_eigenspectrum(L, method="full")
                _save_to_cache(cache_dir, key, eigs)
            except Exception as e:
                if verbose:
                    warnings.warn(f"  {sub_id}: {e}")
                continue
        spectra.append((sub, eigs))
    return spectra


# ─────────────────────────────────────────────────────────────────────────────
# TEST A: THREE-COMPONENT VARIANCE ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def generate_chung_lu_spectrum(A, n_samples=20, density=0.15, seed=42):
    """
    Chung-Lu configuration model spectrum at target density.
    Returns (mean_spectrum, std_spectrum).
    """
    rng = np.random.default_rng(seed)
    A_bin = _threshold_adjacency(A, target_density=density)
    N = A_bin.shape[0]
    deg = A_bin.sum(axis=1)
    total = deg.sum()
    if total < 2:
        return np.zeros(N), np.zeros(N)

    samples = []
    for _ in range(n_samples):
        p = np.outer(deg, deg) / total
        np.clip(p, 0, 1, out=p)
        np.fill_diagonal(p, 0)
        r = rng.random((N, N))
        A_cl = np.triu(r < p, 1)
        A_cl = A_cl + A_cl.T
        L = np.diag(A_cl.sum(1)) - A_cl
        e = eigh(L, eigvals_only=True)
        samples.append(np.sort(np.maximum(e, 0)))

    return np.mean(samples, 0), np.std(samples, 0)


def compute_three_component_analysis(subjects, cache_dir=None, n_cl_samples=15,
                                      density=0.15, verbose=True):
    """
    TEST A: Decompose spectral variance into three interpretable components.

    Component 1: Between-subject CL variance
        If near zero → universality is enforced by shared degree-constraint template
        (all human brains share the same degree-sequence spectral archetype)

    Component 2: Within-subject residual (actual - CL) per subject
        Captures higher-order structure beyond degree sequence

    Component 3: Between-subject residual variance
        If >0 and correlated with diagnosis → individuated component is real

    Scientific interpretation:
        Low between-CL variance + high within-corr → universality is degree-constrained
        Residual correlated with diagnosis → PMIR captures clinically relevant individuation
    """
    if verbose:
        print(f"\n[TEST A] Three-Component Variance Analysis")
        print(f"  CL density: {density:.0%}, samples per subject: {n_cl_samples}")
        print(f"  N subjects: {len(subjects)}")

    n_q = 200
    q_grid = np.linspace(0, 1, n_q)

    actual_curves, cl_curves, lambda2_vals = [], [], []
    subject_ids, diagnosis_labels = [], []

    spectra = _get_eigenspectra(subjects, cache_dir, verbose=False)

    for i, (sub, eigs) in enumerate(spectra):
        if verbose and i % 50 == 0:
            print(f"  [{i+1}/{len(spectra)}] {sub['subject_id']}")
        try:
            lam2 = get_lambda2(eigs)
            ac = _to_shape_curve(eigs / lam2, q_grid)

            cl_mean, _ = generate_chung_lu_spectrum(
                sub["adjacency_matrix"], n_samples=n_cl_samples, density=density)
            cl_lam2 = get_lambda2(cl_mean)
            dc = _to_shape_curve(cl_mean / cl_lam2, q_grid)

            if ac is None or dc is None:
                continue

            actual_curves.append(ac)
            cl_curves.append(dc)
            lambda2_vals.append(lam2)
            subject_ids.append(sub["subject_id"])
            diagnosis_labels.append(sub.get("metadata", {}).get("diagnosis"))

        except Exception as e:
            warnings.warn(f"  {sub['subject_id']}: {e}")

    if len(actual_curves) < 10:
        print("[TEST A] Insufficient subjects.")
        return None

    A_mat = np.array(actual_curves)   # (n, 200) actual shape curves
    D_mat = np.array(cl_curves)       # (n, 200) CL shape curves

    # Variance components
    var_actual_between   = float(A_mat.var(axis=0).mean())
    var_cl_between       = float(D_mat.var(axis=0).mean())   # KEY: should be near 0
    residuals            = A_mat - D_mat                      # (n, 200)
    var_residual_between = float(residuals.var(axis=0).mean())

    # Within-subject: how well does CL predict actual PER SUBJECT?
    within_corrs = [pearsonr(a, d)[0] for a, d in zip(actual_curves, cl_curves)]
    mean_within_corr = float(np.mean(within_corrs))

    # Residual magnitude per subject
    residual_magnitudes = np.sqrt((residuals**2).mean(axis=1))

    # Does residual magnitude correlate with diagnosis?
    diag_correlation = None
    if any(d is not None for d in diagnosis_labels):
        dx_num = np.array([1 if d == 1 else (0 if d == 2 else np.nan)
                           for d in diagnosis_labels])
        valid = ~np.isnan(dx_num)
        if valid.sum() > 10 and dx_num[valid].std() > 0:
            r_dx, p_dx = spearmanr(residual_magnitudes[valid], dx_num[valid])
            diag_correlation = {"r": float(r_dx), "p": float(p_dx),
                                 "n": int(valid.sum())}

    # CL convergence: do all CL curves converge to a single archetype?
    cl_mean_curve  = D_mat.mean(axis=0)
    cl_spread_at_q = D_mat.std(axis=0)
    cl_convergence = float(cl_spread_at_q.mean())  # near 0 = all CL same

    if verbose:
        print(f"\n  [TEST A RESULTS]")
        print(f"  N subjects:                      {len(actual_curves)}")
        print(f"  Between-subject actual var:      {var_actual_between:.6f}")
        print(f"  Between-subject CL var:          {var_cl_between:.6f}")
        print(f"  Between-subject residual var:    {var_residual_between:.6f}")
        print(f"  CL mean spread (convergence):    {cl_convergence:.6f}  "
              f"({'near-zero = universal archetype' if cl_convergence < 0.01 else 'high = CL varies'})")
        print(f"  Within-subject corr (actual~CL): r = {mean_within_corr:.4f}")
        print(f"  Within-subject R²:               {mean_within_corr**2*100:.1f}%  "
              f"(degree explains this fraction of per-subject spectrum)")
        if diag_correlation:
            dc = diag_correlation
            print(f"  Residual vs diagnosis:           "
                  f"r={dc['r']:.4f}, p={dc['p']:.4f}, n={dc['n']}")
            sig = "SIGNIFICANT" if dc['p'] < 0.05 else "not significant"
            print(f"  -> Individuated component is {sig}")

    return {
        "n_subjects": len(actual_curves),
        "actual_curves": A_mat,
        "cl_curves": D_mat,
        "residuals": residuals,
        "residual_magnitudes": residual_magnitudes,
        "var_actual_between": var_actual_between,
        "var_cl_between": var_cl_between,
        "var_residual_between": var_residual_between,
        "cl_convergence": cl_convergence,
        "within_subject_corr": mean_within_corr,
        "within_subject_r2": mean_within_corr**2,
        "within_subject_corrs_all": within_corrs,
        "diag_correlation": diag_correlation,
        "lambda2_values": np.array(lambda2_vals),
        "subject_ids": subject_ids,
        "diagnosis_labels": diagnosis_labels,
        "density_used": density,
    }


# ─────────────────────────────────────────────────────────────────────────────
# TEST B: EIGENVALUE STABILITY + RMSD LANDSCAPE
# ─────────────────────────────────────────────────────────────────────────────

def scan_eigenvalue_stability(subjects, cache_dir=None, n_subjects_sample=100,
                               verbose=True, seed=42):
    """
    TEST B: Eigenvalue stability analysis — redesigned from landscape scan.

    INSIGHT FROM v1/v2: fMRI spectra lie on a 1D (scale) manifold, so CV of
    rescaled spectra is identical for all rescaling parameters. Need a different
    question.

    TWO COMPLEMENTARY TESTS:

    B1. Raw eigenvalue stability (no rescaling):
        For each rank k, compute CV(lambda_k) across subjects.
        Lower CV = more stable = more reproducible eigenvalue.
        Lambda2 should be stable relative to its mean if it's a natural
        reference point (the Fiedler value reflects integration timescale).

    B2. RMSD landscape:
        For each rescaling parameter, compute mean RMSD from the grand-mean
        rescaled curve (NOT CV). RMSD is sensitive to absolute deviations,
        not just relative variation. Lambda2 should minimize RMSD if it
        aligns the spectra better than other parameters in absolute terms.

    Returns: B1 stability profile, B2 RMSD landscape, combined verdict.
    """
    rng = np.random.default_rng(seed)
    if verbose:
        print(f"\n[TEST B] Eigenvalue Stability + RMSD Landscape")
        print(f"  Subsampling {n_subjects_sample} subjects...")

    spectra = _get_eigenspectra(subjects, cache_dir, verbose=False)
    if len(spectra) > n_subjects_sample:
        idxs = rng.choice(len(spectra), n_subjects_sample, replace=False)
        spectra = [spectra[i] for i in idxs]

    if verbose:
        print(f"  Loaded {len(spectra)} spectra")

    eigenspectra_raw = [e for _, e in spectra]
    min_N = min(len(e[e > 1e-10]) for e in eigenspectra_raw)
    max_rank = min(min_N - 1, 50)

    # ── B1: Raw eigenvalue stability ──────────────────────────────────────────
    stability_cv   = []
    stability_mean = []
    stability_std  = []

    for k in range(1, max_rank + 1):
        vals = []
        for eigs in eigenspectra_raw:
            pos = eigs[eigs > 1e-10]
            if k <= len(pos):
                vals.append(pos[k-1])
        if len(vals) < 5:
            stability_cv.append(np.nan)
            stability_mean.append(np.nan)
            stability_std.append(np.nan)
            continue
        vals = np.array(vals)
        mu = vals.mean()
        sd = vals.std()
        stability_cv.append(float(sd / mu) if mu > 0 else np.nan)
        stability_mean.append(float(mu))
        stability_std.append(float(sd))

    stability_cv = np.array(stability_cv)
    best_stability_rank = int(np.nanargmin(stability_cv)) + 1

    # ── B2: RMSD landscape ───────────────────────────────────────────────────
    n_q = 200
    q_grid = np.linspace(0, 1, n_q)
    rmsd_scores = []

    for k in range(1, max_rank + 1):
        curves = []
        for eigs in eigenspectra_raw:
            pos = eigs[eigs > 1e-10]
            if k <= len(pos) and pos[k-1] > 1e-10:
                rescaled = eigs / pos[k-1]
                c = _to_shape_curve(rescaled, q_grid)
                if c is not None:
                    curves.append(c)
        if len(curves) < 5:
            rmsd_scores.append(np.nan)
            continue
        C = np.array(curves)
        grand_mean = C.mean(axis=0)
        rmsd = float(np.sqrt(((C - grand_mean)**2).mean()))
        rmsd_scores.append(rmsd)

    rmsd_scores = np.array(rmsd_scores)
    best_rmsd_rank = int(np.nanargmin(rmsd_scores)) + 1

    # ── Named candidate RMSD ─────────────────────────────────────────────────
    def named_candidates(eigs):
        pos = eigs[eigs > 1e-10]
        N = len(pos)
        if N < 4:
            return {}
        return {
            "lambda_2":    pos[0],
            "lambda_3":    pos[1],
            "lambda_4":    pos[2],
            "lambda_max":  pos[-1],
            "lambda_N/2":  pos[N // 2],
            "lambda_N/4":  pos[N // 4],
            "mean":        pos.mean(),
            "median":      float(np.median(pos)),
        }

    named_buckets = {}
    for eigs in eigenspectra_raw:
        for name, val in named_candidates(eigs).items():
            if val > 1e-10:
                c = _to_shape_curve(eigs / val, q_grid)
                if c is not None:
                    named_buckets.setdefault(name, []).append(c)

    named_rmsd = {}
    for name, curves in named_buckets.items():
        C = np.array(curves)
        grand_mean = C.mean(axis=0)
        named_rmsd[name] = float(np.sqrt(((C - grand_mean)**2).mean()))

    lambda2_rmsd_rank = sum(1 for v in named_rmsd.values()
                             if v < named_rmsd.get("lambda_2", np.inf)) + 1

    if verbose:
        print(f"\n  [TEST B1: Raw Eigenvalue Stability (CV across subjects)]")
        print(f"  Rank k=1 (lambda2) CV:   {stability_cv[0]:.4f}")
        print(f"  Min CV at rank:          k = {best_stability_rank}  "
              f"(CV = {stability_cv[best_stability_rank-1]:.4f})")
        print(f"  Lambda2 stability rank:  "
              f"{'#1 most stable' if best_stability_rank == 1 else f'#{best_stability_rank}'}")

        print(f"\n  [TEST B2: RMSD Landscape (shape deviation from grand mean)]")
        print(f"  Lambda2 (k=1) RMSD:  {rmsd_scores[0]:.6f}")
        print(f"  Minimum RMSD at:     k = {best_rmsd_rank}  "
              f"(RMSD = {rmsd_scores[best_rmsd_rank-1]:.6f})")
        print(f"\n  Named candidate RMSD scores (lower = better alignment):")
        for name, v in sorted(named_rmsd.items(), key=lambda x: x[1]):
            marker = "  ← PMIR" if name == "lambda_2" else ""
            print(f"    {name:<22} RMSD = {v:.6f}{marker}")
        print(f"\n  Lambda2 RMSD rank among named candidates: #{lambda2_rmsd_rank}")

    return {
        # B1
        "stability_cv": stability_cv,
        "stability_mean": stability_mean,
        "stability_std": stability_std,
        "best_stability_rank": best_stability_rank,
        "lambda2_stability_cv": float(stability_cv[0]),
        # B2
        "rmsd_scores": rmsd_scores,
        "best_rmsd_rank": best_rmsd_rank,
        "lambda2_rmsd": float(rmsd_scores[0]),
        "minimum_rmsd": float(np.nanmin(rmsd_scores)),
        "named_rmsd": named_rmsd,
        "lambda2_rmsd_rank_among_named": lambda2_rmsd_rank,
        "n_named_candidates": len(named_rmsd),
        "is_lambda2_rmsd_minimum": best_rmsd_rank == 1,
        "n_subjects_scanned": len(spectra),
        "max_rank_scanned": max_rank,
    }


# ─────────────────────────────────────────────────────────────────────────────
# TEST C: SITE-BASED REPLICATION WITHIN ABIDE
# ─────────────────────────────────────────────────────────────────────────────

def split_abide_by_site(subjects):
    """
    Split ABIDE subjects by acquisition site.
    Site is encoded in subject_id prefix (e.g. 'Pitt_0050003' → 'Pitt').
    Returns dict: {site_name: [subjects]}
    """
    sites = {}
    for sub in subjects:
        sid = sub["subject_id"]
        # Try to extract site from ID (format: SiteName_SubjectID)
        parts = sid.split("_")
        if len(parts) >= 2 and not parts[0].isdigit():
            site = parts[0]
        else:
            # Numeric ID — look in metadata or use "unknown"
            site = sub.get("metadata", {}).get("site", "unknown")
        sites.setdefault(site, []).append(sub)
    return sites


def run_site_replication(subjects, cache_dir=None, min_per_site=10, verbose=True):
    """
    TEST C: Replicate spectral universality across ABIDE acquisition sites.

    Different sites = different scanners, protocols, slice timing, TR.
    If universality holds across sites, it cannot be explained by acquisition
    artifact — it's a genuine property of brain functional connectivity.

    Selects the two largest sites with >= min_per_site subjects each.
    Compares their collapse scores and mean correlations.

    Also splits by diagnosis within each site if both ASD and control
    subjects are present.
    """
    if verbose:
        print(f"\n[TEST C] Site-Based Replication within ABIDE")

    sites = split_abide_by_site(subjects)
    viable = {s: subs for s, subs in sites.items()
              if len(subs) >= min_per_site}

    if verbose:
        print(f"  Sites found: {len(sites)}")
        for s, subs in sorted(sites.items(), key=lambda x: -len(x[1])):
            print(f"    {s}: {len(subs)} subjects  "
                  f"{'[viable]' if s in viable else '[too small]'}")

    if len(viable) < 2:
        print(f"[TEST C] Need >= 2 sites with >= {min_per_site} subjects.")
        print(f"  Falling back to diagnosis split (ASD vs Control)...")
        return _diagnosis_split_replication(subjects, cache_dir, verbose)

    # Pick two largest sites
    sorted_sites = sorted(viable.items(), key=lambda x: -len(x[1]))
    site_a_name, site_a_subs = sorted_sites[0]
    site_b_name, site_b_subs = sorted_sites[1]

    if verbose:
        print(f"\n  Comparing: {site_a_name} (n={len(site_a_subs)}) "
              f"vs {site_b_name} (n={len(site_b_subs)})")

    from .spectral_analysis import compute_spectral_universality, compute_collapse_score

    if verbose:
        print(f"\n  --- {site_a_name} ---")
    res_a = compute_spectral_universality(site_a_subs, "lambda2",
                                           cache_dir=cache_dir, verbose=verbose)

    if verbose:
        print(f"\n  --- {site_b_name} ---")
    res_b = compute_spectral_universality(site_b_subs, "lambda2",
                                           cache_dir=cache_dir, verbose=verbose)

    if res_a is None or res_b is None:
        return None

    combined = compute_collapse_score(res_a["rescaled_spectra"] +
                                       res_b["rescaled_spectra"])

    both_r      = res_a["mean_correlation"] > 0.95 and res_b["mean_correlation"] > 0.95
    cv_match    = abs(res_a["collapse_score"] - res_b["collapse_score"]) < 0.05
    combined_ok = combined["collapse_score"] < 0.25

    if verbose:
        print(f"\n  [TEST C RESULTS]")
        print(f"  {'Site':<18} {'N':<8} {'Mean r':<10} {'Collapse CV'}")
        print(f"  {'-'*50}")
        for name, res in [(site_a_name, res_a), (site_b_name, res_b)]:
            print(f"  {name:<18} {res['n_subjects']:<8} "
                  f"{res['mean_correlation']:<10.4f} {res['collapse_score']:.4f}")
        print(f"\n  Combined pool CV: {combined['collapse_score']:.4f}")
        ok = lambda b: "[OK]" if b else "[XX]"
        print(f"  {ok(both_r)} Both sites r > 0.95")
        print(f"  {ok(cv_match)} CV consistent (diff < 0.05)")
        print(f"  {ok(combined_ok)} Combined CV < 0.25")
        n_pass = sum([both_r, cv_match, combined_ok])
        verdict = "REPLICATED" if n_pass == 3 else f"PARTIAL ({n_pass}/3)"
        print(f"\n  VERDICT: {verdict}")

    return {
        "replication_type": "site",
        "primary_name": site_a_name,
        "secondary_name": site_b_name,
        "primary": res_a,
        "secondary": res_b,
        "all_sites": {s: len(subs) for s, subs in sites.items()},
        "combined_collapse": combined,
        "replication_checks": {
            "both_r_above_095": both_r,
            "cv_consistent": cv_match,
            "combined_ok": combined_ok,
        },
    }


def _diagnosis_split_replication(subjects, cache_dir, verbose):
    """Fallback: split by diagnosis if site split unavailable."""
    from .spectral_analysis import compute_spectral_universality, compute_collapse_score

    asd  = [s for s in subjects if s.get("metadata", {}).get("diagnosis") == 1]
    ctrl = [s for s in subjects if s.get("metadata", {}).get("diagnosis") == 2]

    if verbose:
        print(f"  ASD: {len(asd)}, Control: {len(ctrl)}")

    if len(asd) < 5 or len(ctrl) < 5:
        print("[TEST C] Insufficient subjects for any replication strategy.")
        return None

    res_asd  = compute_spectral_universality(asd,  "lambda2",
                                              cache_dir=cache_dir, verbose=verbose)
    res_ctrl = compute_spectral_universality(ctrl, "lambda2",
                                              cache_dir=cache_dir, verbose=verbose)

    if res_asd is None or res_ctrl is None:
        return None

    combined = compute_collapse_score(res_asd["rescaled_spectra"] +
                                       res_ctrl["rescaled_spectra"])

    both_r   = res_asd["mean_correlation"] > 0.95 and res_ctrl["mean_correlation"] > 0.95
    cv_match = abs(res_asd["collapse_score"] - res_ctrl["collapse_score"]) < 0.05
    combined_ok = combined["collapse_score"] < 0.25

    if verbose:
        print(f"\n  [TEST C RESULTS — diagnosis split]")
        for name, res in [("ASD", res_asd), ("Control", res_ctrl)]:
            print(f"  {name:<12} n={res['n_subjects']:<6} "
                  f"r={res['mean_correlation']:.4f}  CV={res['collapse_score']:.4f}")
        print(f"  Combined CV: {combined['collapse_score']:.4f}")
        ok = lambda b: "[OK]" if b else "[XX]"
        print(f"  {ok(both_r)} Both r > 0.95  "
              f"{ok(cv_match)} CV consistent  "
              f"{ok(combined_ok)} Combined OK")

    return {
        "replication_type": "diagnosis",
        "primary_name": "ASD",
        "secondary_name": "Control",
        "primary": res_asd,
        "secondary": res_ctrl,
        "combined_collapse": combined,
        "replication_checks": {
            "both_r_above_095": both_r,
            "cv_consistent": cv_match,
            "combined_ok": combined_ok,
        },
    }
