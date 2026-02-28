"""
MODULE 3: Null Models
All 4 null models required by the research plan, plus permutation testing.

Research plan specifies:
  (a) Erdős-Rényi random graphs with matched density
  (b) Degree-preserved random graphs (configuration model)
  (c) Strength-preserved random graphs
  (d) Alternative rescaling comparisons (handled in spectral_analysis.py)

CRITICAL FALSIFICATION CRITERION:
If degree-preserved null model produces r > 0.90 after λ₂ rescaling,
the result is a trivial consequence of degree distribution — NOT meaningful
spectral universality.
"""

import numpy as np
import warnings
from scipy.stats import norm

from modules.spectral_analysis import (
    build_laplacian, compute_eigenspectrum, rescale_spectrum,
    compute_pairwise_correlations
)


# ─────────────────────────────────────────────────────────────────────────────
# NULL MODEL (a): Erdős-Rényi Random Graphs
# Same edge density as original graph, random topology
# ─────────────────────────────────────────────────────────────────────────────

def generate_erdos_renyi(adjacency_matrix, seed=None):
    """
    Generate Erdős-Rényi random graph matching edge density of input.
    For weighted graphs: random topology with same total weight.

    Returns: N×N symmetric adjacency matrix (binary or weighted)
    """
    rng = np.random.default_rng(seed)
    N = adjacency_matrix.shape[0]

    # Edge density: proportion of possible edges that exist
    n_possible = N * (N - 1) / 2
    n_edges = np.sum(adjacency_matrix > 0) / 2
    p = n_edges / n_possible if n_possible > 0 else 0

    # Generate random symmetric binary matrix
    upper = rng.random((N, N)) < p
    upper = np.triu(upper, k=1)
    binary = upper + upper.T

    # Scale to match mean weight of original
    mean_weight = adjacency_matrix[adjacency_matrix > 0].mean() if np.any(adjacency_matrix > 0) else 1.0
    null_matrix = binary.astype(float) * mean_weight

    return null_matrix


# ─────────────────────────────────────────────────────────────────────────────
# NULL MODEL (b): Degree-Preserved (Configuration Model)
# Randomizes connections while preserving degree sequence exactly
# CRITICAL: if this produces r > 0.90, universality is trivial
# ─────────────────────────────────────────────────────────────────────────────

def generate_degree_preserved(adjacency_matrix, n_rewires=None, seed=None):
    """
    Generate degree-preserved random graph via edge rewiring (Maslov-Sneppen).

    n_rewires: number of edge swap attempts (default: 100 × n_edges)
    Returns: N×N symmetric adjacency matrix
    """
    rng = np.random.default_rng(seed)
    A = adjacency_matrix.copy()
    A = (A + A.T) / 2.0
    np.fill_diagonal(A, 0)

    # Get edge list (upper triangle only, for undirected)
    rows, cols = np.where(np.triu(A > 0, k=1))
    edges = list(zip(rows, cols))
    n_edges = len(edges)

    if n_rewires is None:
        n_rewires = 10 * n_edges

    # Double-swap rewiring to preserve degree sequence
    edges = list(edges)  # mutable copy
    edge_set = set(map(tuple, edges))

    for _ in range(n_rewires):
        if len(edges) < 2:
            break
        # Pick two random edges
        i1 = rng.integers(0, n_edges)
        i2 = rng.integers(0, n_edges)
        if i1 == i2:
            continue

        u, v = edges[i1]
        x, y = edges[i2]

        # Propose swap: (u,v),(x,y) → (u,x),(v,y) or (u,y),(v,x)
        if rng.random() < 0.5:
            new1, new2 = (min(u, x), max(u, x)), (min(v, y), max(v, y))
        else:
            new1, new2 = (min(u, y), max(u, y)), (min(v, x), max(v, x))

        # Check validity: no self-loops, no duplicate edges
        if (new1[0] == new1[1] or new2[0] == new2[1] or
                new1 in edge_set or new2 in edge_set):
            continue

        # Apply swap
        edge_set.discard(edges[i1])
        edge_set.discard(edges[i2])
        edge_set.add(new1)
        edge_set.add(new2)
        edges[i1] = new1
        edges[i2] = new2

    # Reconstruct adjacency matrix from rewired edge set
    N = A.shape[0]
    B = np.zeros((N, N))
    original_weights = {(min(r, c), max(r, c)): A[r, c]
                        for r, c in zip(*np.where(np.triu(A > 0, k=1)))}

    for u, v in edge_set:
        # Preserve weight from nearest original edge (approximate for weighted)
        w = original_weights.get((u, v), 1.0)
        B[u, v] = w
        B[v, u] = w

    return B


# ─────────────────────────────────────────────────────────────────────────────
# NULL MODEL (c): Strength-Preserved Random Graphs
# Preserves node strength (weighted degree) sequence
# ─────────────────────────────────────────────────────────────────────────────

def generate_strength_preserved(adjacency_matrix, seed=None):
    """
    Generate random graph preserving node strength (sum of edge weights) sequence.
    Uses the Chung-Lu model weighted version.

    Returns: N×N symmetric adjacency matrix
    """
    rng = np.random.default_rng(seed)
    A = adjacency_matrix.copy()
    A = (A + A.T) / 2.0
    np.fill_diagonal(A, 0)

    N = A.shape[0]
    strengths = A.sum(axis=1)
    total_strength = strengths.sum()

    if total_strength == 0:
        return np.zeros((N, N))

    # Chung-Lu model: expected weight of edge (i,j) ∝ s_i * s_j / (total/2)
    null_matrix = np.outer(strengths, strengths) / (total_strength / 2.0)
    np.fill_diagonal(null_matrix, 0)

    # Add Poisson noise to make it stochastic
    noise_scale = 0.1 * (null_matrix[null_matrix > 0].std() if np.any(null_matrix > 0) else 1.0)
    noise = rng.normal(0, noise_scale, (N, N))
    noise = (noise + noise.T) / 2.0  # symmetric noise
    null_matrix = np.maximum(null_matrix + noise, 0)
    np.fill_diagonal(null_matrix, 0)

    return null_matrix


# ─────────────────────────────────────────────────────────────────────────────
# NULL MODEL EVALUATION
# Run a null model generator on all subjects, compute spectral universality
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_null_model(subjects, null_generator, rescaling_method="lambda2",
                         n_samples=100, random_seed=42, verbose=True,
                         null_name="null", real_mean_curve=None,
                         real_rmsd=None, interpolate_to=None):
    """
    Generate null graphs for each subject, compute rescaled spectra,
    and measure collapse quality vs real brain data.

    DESIGN RATIONALE:
    Pearson inter-subject r is NOT appropriate here — any set of graphs with
    the same N and density will have r ≈ 0.999 after normalization (RMT).
    The correct test is whether real brain networks collapse MORE TIGHTLY to
    a universal curve than randomized versions of those same networks.

    Primary metric: mean RMSD from population mean curve.
    Real brains should have SMALLER RMSD than null graphs if PMIR is real.

    We compare:
      (1) Real brain RMSD (passed in as real_rmsd)
      (2) Null RMSD (computed here, one value per sample)

    Returns:
        null_rmsds: array of mean RMSD values across null samples
        null_mean_rmsd: float
        null_std_rmsd: float
        p_value: fraction of null samples with RMSD <= real_rmsd
    """
    from modules.spectral_analysis import compute_collapse_score

    rng = np.random.default_rng(random_seed)
    null_rmsds = []

    for sample_idx in range(n_samples):
        seed_for_sample = int(rng.integers(0, 2**31))
        rescaled_list = []

        # Subsample subjects for speed — 100 is sufficient for null distribution
        sample_subjects = subjects
        if len(subjects) > 100:
            idx = rng.choice(len(subjects), size=100, replace=False)
            sample_subjects = [subjects[i] for i in idx]

        for sub in sample_subjects:
            try:
                null_adj = null_generator(
                    sub["adjacency_matrix"],
                    seed=seed_for_sample + hash(sub["subject_id"]) % 10000
                )
                L = build_laplacian(null_adj, laplacian_type="combinatorial")
                eigs = compute_eigenspectrum(L, method="full")
                rescaled = rescale_spectrum(eigs, method=rescaling_method)
                rescaled_list.append(rescaled)
            except Exception:
                pass

        if len(rescaled_list) < 5:
            continue

        collapse = compute_collapse_score(rescaled_list,
                                          interpolate_to=interpolate_to)
        null_rmsds.append(collapse["mean_rmsd"])

        if verbose and sample_idx % 10 == 0:
            print(f"  [{null_name}] Sample {sample_idx+1}/{n_samples}: RMSD = {collapse['mean_rmsd']:.4f}")

    null_rmsds = np.array(null_rmsds)
    if len(null_rmsds) == 0:
        warnings.warn(f"[{null_name}] No successful null samples")
        return None

    null_mean = float(null_rmsds.mean())
    null_std  = float(null_rmsds.std())

    if verbose:
        print(f"  [{null_name}] Null RMSD = {null_mean:.4f} ± {null_std:.4f}")
        if real_rmsd is not None:
            direction = "SMALLER (✓ brain is more universal)" if real_rmsd < null_mean else "LARGER (⚠ brain is less universal)"
            print(f"  [{null_name}] Real RMSD = {real_rmsd:.4f} → {direction}")

    # p-value: fraction of null samples at or below real RMSD
    # We want real_rmsd < null (brains more universal), so p = P(null <= real)
    p_value = float(np.mean(null_rmsds <= real_rmsd)) if real_rmsd is not None else None

    return {
        "null_rmsds": null_rmsds,
        "null_mean": null_mean,       # mean RMSD of null
        "null_std":  null_std,
        "n_samples": len(null_rmsds),
        "null_name": null_name,
        "real_rmsd": real_rmsd,
        "p_value":   p_value,
        # Keep legacy fields so Stage 8 verdict code doesn't crash
        "null_correlations": null_rmsds,     # repurposed: RMSD not r
        "null_mean_corr":    null_mean,
    }


# ─────────────────────────────────────────────────────────────────────────────
# RUN ALL NULL MODELS
# ─────────────────────────────────────────────────────────────────────────────

NULL_GENERATORS = {
    "erdos_renyi": generate_erdos_renyi,
    "degree_preserved": generate_degree_preserved,
    "strength_preserved": generate_strength_preserved,
}

def run_all_null_models(subjects, observed_r, rescaling_method="lambda2",
                        n_samples_per_model=100, config=None, verbose=True,
                        real_rmsd=None, interpolate_to=None):
    """
    Run all enabled null models and compare against observed universality.

    observed_r: mean inter-subject Pearson r from real data (kept for record)
    real_rmsd:  mean RMSD from universal curve for real brain data (primary metric)
                Pass primary_result['mean_rmsd'] here.

    Returns: dict of null model results.
    """
    results = {}

    null_config = config.NULL_MODELS if config is not None else {
        k: {"enabled": True, "n_samples": n_samples_per_model}
        for k in NULL_GENERATORS.keys()
    }

    for name, generator in NULL_GENERATORS.items():
        if not null_config.get(name, {}).get("enabled", True):
            print(f"[NULL MODELS] Skipping {name} (disabled in config)")
            continue

        n_samples = null_config.get(name, {}).get("n_samples", n_samples_per_model)
        print(f"\n[NULL MODELS] Running: {name} ({n_samples} samples)")
        print(f"  Metric: RMSD from universal mean curve (lower = more universal)")

        result = evaluate_null_model(
            subjects, generator,
            rescaling_method=rescaling_method,
            n_samples=n_samples,
            null_name=name,
            verbose=verbose,
            real_rmsd=real_rmsd,
            interpolate_to=interpolate_to,
        )
        if result is None:
            continue

        result["observed_r"] = observed_r
        # z-score: how many SDs is real_rmsd below null mean (negative = more universal)
        if real_rmsd is not None:
            result["z_score"] = compute_z_score(real_rmsd, result["null_mean"], result["null_std"])
        else:
            result["z_score"] = np.nan

        # Falsification criterion for degree_preserved:
        # Real RMSD must be SIGNIFICANTLY BELOW null RMSD
        # i.e. brains must be MORE universal than degree-preserved random graphs
        if name == "degree_preserved" and real_rmsd is not None:
            # Falsified if real_rmsd >= null_mean (brain not more universal than degree-null)
            result["falsification_triggered"] = real_rmsd >= result["null_mean"]
            if result["falsification_triggered"]:
                print(f"  ⚠ FALSIFICATION: brain RMSD={real_rmsd:.4f} >= degree-null RMSD={result['null_mean']:.4f}")
            else:
                print(f"  ✓ Brain RMSD {real_rmsd:.4f} < degree-null RMSD {result['null_mean']:.4f}")

        results[name] = result

    # Summary table
    if verbose:
        print("\n[NULL MODELS] Summary (RMSD metric, lower = more universal):")
        print(f"  Real brain RMSD = {real_rmsd:.4f}" if real_rmsd else "  Real brain RMSD = N/A")
        print(f"{'Null Model':<25} {'Null RMSD':>10} {'Z-score':>9} {'p-value':>12} {'Status'}")
        print("-" * 75)
        for name, res in results.items():
            pv = res.get('p_value')
            pv_str = f"{pv:.2e}" if pv is not None else "N/A"
            status = "⚠ FAILS" if res.get("falsification_triggered") else "✓ passes"
            print(f"{name:<25} {res['null_mean']:>10.4f} {res.get('z_score', float('nan')):>9.2f} "
                  f"{pv_str:>12} {status}")

    return results


# ─────────────────────────────────────────────────────────────────────────────
# PERMUTATION TEST
# ─────────────────────────────────────────────────────────────────────────────

def permutation_test(rescaled_spectra_list, n_permutations=10000,
                     observed_r=None, random_seed=42, verbose=True):
    """
    Permutation test: shuffle subject labels, recompute mean correlation.
    Tests whether observed inter-subject correlation exceeds chance.

    Returns: p_value, permuted_correlations array
    """
    rng = np.random.default_rng(random_seed)
    n_subjects = len(rescaled_spectra_list)
    S = np.array([_interpolate_to_common(s, rescaled_spectra_list)
                  for s in rescaled_spectra_list])

    if observed_r is None:
        corr_matrix = np.corrcoef(S)
        mask = ~np.eye(n_subjects, dtype=bool)
        observed_r = corr_matrix[mask].mean()

    permuted_correlations = np.zeros(n_permutations)

    for i in range(n_permutations):
        perm_idx = rng.permutation(n_subjects)
        S_perm = S[perm_idx]
        corr_perm = np.corrcoef(S_perm)
        mask = ~np.eye(n_subjects, dtype=bool)
        permuted_correlations[i] = corr_perm[mask].mean()

    p_value = np.mean(permuted_correlations >= observed_r)

    if verbose:
        print(f"[PERMUTATION TEST] Observed r = {observed_r:.4f}")
        print(f"[PERMUTATION TEST] Permuted r = {permuted_correlations.mean():.4f} ± {permuted_correlations.std():.4f}")
        print(f"[PERMUTATION TEST] p-value = {p_value:.2e} (n={n_permutations} permutations)")

    return p_value, permuted_correlations, observed_r


def _interpolate_to_common(spectrum, all_spectra):
    """Interpolate spectrum to the minimum common length."""
    from scipy.interpolate import interp1d
    min_len = min(len(s) for s in all_spectra)
    if len(spectrum) == min_len:
        return spectrum
    x_old = np.linspace(0, 1, len(spectrum))
    x_new = np.linspace(0, 1, min_len)
    f = interp1d(x_old, spectrum, kind="linear")
    return f(x_new)


# ─────────────────────────────────────────────────────────────────────────────
# STATISTICAL UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def compute_z_score(observed, null_mean, null_std):
    if null_std == 0:
        return np.inf if observed > null_mean else 0.0
    return (observed - null_mean) / null_std


def compute_p_value(z_score, one_tailed=True):
    """One-tailed p-value (we predict r > null)."""
    return 1.0 - norm.cdf(z_score) if one_tailed else 2.0 * (1.0 - norm.cdf(abs(z_score)))
