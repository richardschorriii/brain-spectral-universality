"""
MODULE 4: Consciousness State Analysis & Parcellation Independence

Tests two core predictions from the research plan:
  1. Universality degrades systematically as consciousness depth increases
     (wake → NREM1 → NREM2 → NREM3 → propofol deep sedation)
  2. Universality is parcellation-independent (holds for 3+ atlases)

Also handles grouping subjects by state for cross-state comparison.
"""

import numpy as np
from scipy.stats import pearsonr, spearmanr
import warnings

from modules.spectral_analysis import compute_spectral_universality


# ─────────────────────────────────────────────────────────────────────────────
# CONSCIOUSNESS STATE ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

# Ordered from most conscious to least — expected universality should decrease
CONSCIOUSNESS_ORDER = [
    "wake",
    "awake",
    "light_sedation",
    "NREM1",
    "NREM2",
    "deep_sedation",
    "NREM3",
]

def group_subjects_by_state(subjects):
    """
    Group subject dicts by their consciousness state.
    Returns: dict {state: [subject_dicts]}
    """
    groups = {}
    for sub in subjects:
        state = sub.get("state", "unknown")
        if state not in groups:
            groups[state] = []
        groups[state].append(sub)

    print(f"[STATE GROUPING] Found {len(groups)} states:")
    for state, subs in groups.items():
        print(f"  {state}: n={len(subs)}")

    return groups


def analyze_consciousness_gradient(subjects, rescaling_method="lambda2",
                                    cache_dir=None, verbose=True):
    """
    Compute spectral universality for each consciousness state and test
    whether it decreases monotonically along the depth gradient.

    Returns:
        state_results: dict {state: spectral_universality_result}
        gradient_test: statistical test of monotonic decrease
    """
    groups = group_subjects_by_state(subjects)

    state_results = {}
    for state, subs in groups.items():
        if len(subs) < 3:
            warnings.warn(f"State {state} has only {len(subs)} subjects — skipping")
            continue

        if verbose:
            print(f"\n[CONSCIOUSNESS] Analyzing state: {state} (n={len(subs)})")

        result = compute_spectral_universality(
            subs, rescaling_method=rescaling_method,
            cache_dir=cache_dir, verbose=verbose
        )
        if result is not None:
            state_results[state] = result

    # Order states by consciousness depth
    ordered_states = [s for s in CONSCIOUSNESS_ORDER if s in state_results]
    unordered = [s for s in state_results if s not in CONSCIOUSNESS_ORDER]
    if unordered:
        warnings.warn(f"States not in ordering: {unordered}")
    ordered_states += unordered

    # Extract ordered correlations
    ordered_r = []
    ordered_labels = []
    for state in ordered_states:
        r = state_results[state]["mean_correlation"]
        ordered_r.append(r)
        ordered_labels.append(state)

    if verbose:
        print("\n[CONSCIOUSNESS GRADIENT] Universality by state (most→least conscious):")
        for state, r in zip(ordered_labels, ordered_r):
            bar = "█" * int(r * 30)
            print(f"  {state:<20} r={r:.4f}  {bar}")

    # Monotonicity test: should universality decrease along gradient?
    gradient_test = None
    if len(ordered_r) >= 3:
        # Spearman correlation: rank of state (0=wake) vs universality r
        depth_ranks = list(range(len(ordered_r)))
        rho, p_mono = spearmanr(depth_ranks, ordered_r)

        # We predict negative Spearman (deeper → lower r)
        # One-tailed test
        gradient_test = {
            "spearman_rho": rho,
            "p_value_two_tailed": p_mono,
            "p_value_one_tailed": p_mono / 2 if rho < 0 else 1.0 - p_mono / 2,
            "expected_direction": "negative (universality decreases with depth)",
            "result": "CONFIRMED" if rho < -0.5 and p_mono < 0.05 else "NOT CONFIRMED",
            "ordered_states": ordered_labels,
            "ordered_r": ordered_r,
        }

        if verbose:
            print(f"\n[CONSCIOUSNESS GRADIENT] Monotonicity test:")
            print(f"  Spearman ρ = {rho:.4f} (expected negative)")
            print(f"  p-value (one-tailed) = {gradient_test['p_value_one_tailed']:.4f}")
            print(f"  Result: {gradient_test['result']}")

    return state_results, gradient_test


# ─────────────────────────────────────────────────────────────────────────────
# PARCELLATION INDEPENDENCE TEST
# ─────────────────────────────────────────────────────────────────────────────

def test_parcellation_independence(subjects_by_parcellation, rescaling_method="lambda2",
                                    cache_dir=None, verbose=True):
    """
    Run spectral universality analysis for each parcellation scheme and
    check whether results are consistent (no single atlas driving the result).

    subjects_by_parcellation: dict {parcellation_name: [subject_dicts]}
        (subjects with connectivity matrices computed at each parcellation)

    Returns: dict of results per parcellation + consistency summary
    """
    parcellation_results = {}

    for parc_name, subs in subjects_by_parcellation.items():
        if len(subs) < 3:
            warnings.warn(f"Parcellation {parc_name}: only {len(subs)} subjects")
            continue

        if verbose:
            print(f"\n[PARCELLATION] Testing: {parc_name} (n={len(subs)} subjects)")

        result = compute_spectral_universality(
            subs, rescaling_method=rescaling_method,
            cache_dir=cache_dir, verbose=verbose
        )
        if result is not None:
            parcellation_results[parc_name] = result

    # Consistency check
    r_values = {k: v["mean_correlation"] for k, v in parcellation_results.items()}

    if verbose:
        print("\n[PARCELLATION INDEPENDENCE] Results per atlas:")
        print(f"{'Parcellation':<20} {'N regions':>10} {'Mean r':>10} {'Status'}")
        print("-" * 55)
        for parc, r in r_values.items():
            # Get n_regions from first subject's adjacency matrix
            n_reg = parcellation_results[parc]["eigenspectra"][0].shape[0] if parcellation_results[parc]["eigenspectra"] else "?"
            status = "✓ > 0.95" if r > 0.95 else ("⚠ 0.80-0.95" if r > 0.80 else "✗ < 0.80")
            print(f"{parc:<20} {str(n_reg):>10} {r:>10.4f} {status}")

    # Falsification check: if r < 0.80 for any parcellation → fails
    failed_parcellations = [k for k, r in r_values.items() if r < 0.80]
    if failed_parcellations:
        print(f"\n⚠ PARCELLATION FALSIFICATION: r < 0.80 for {failed_parcellations}")
    else:
        n_above_threshold = sum(1 for r in r_values.values() if r > 0.95)
        print(f"\n✓ Parcellation independence: {n_above_threshold}/{len(r_values)} parcellations r > 0.95")

    consistency = {
        "r_values": r_values,
        "min_r": min(r_values.values()) if r_values else None,
        "max_r": max(r_values.values()) if r_values else None,
        "range": max(r_values.values()) - min(r_values.values()) if r_values else None,
        "n_parcellations_tested": len(r_values),
        "n_above_0.95": sum(1 for r in r_values.values() if r > 0.95),
        "falsification_triggered": len(failed_parcellations) > 0,
        "failed_parcellations": failed_parcellations,
    }

    return parcellation_results, consistency


# ─────────────────────────────────────────────────────────────────────────────
# CONSCIOUSNESS DROP QUANTIFICATION
# Measure the size of universality drop as function of consciousness depth
# ─────────────────────────────────────────────────────────────────────────────

def quantify_universality_drop(gradient_test_result):
    """
    From the consciousness gradient test, compute:
    - Δr from wake to deepest state
    - Drop rate per consciousness stage
    - Whether the drop is statistically significant and monotonic

    Returns: summary dict
    """
    if gradient_test_result is None:
        return None

    ordered_r = gradient_test_result["ordered_r"]
    ordered_states = gradient_test_result["ordered_states"]

    if len(ordered_r) < 2:
        return None

    wake_r = ordered_r[0]
    deepest_r = ordered_r[-1]
    delta_r = wake_r - deepest_r
    drop_per_stage = delta_r / (len(ordered_r) - 1) if len(ordered_r) > 1 else 0

    # Count how many transitions show decrease
    n_decreases = sum(1 for i in range(1, len(ordered_r)) if ordered_r[i] < ordered_r[i-1])
    n_transitions = len(ordered_r) - 1
    monotonicity_fraction = n_decreases / n_transitions if n_transitions > 0 else 0

    return {
        "wake_r": wake_r,
        "deepest_r": deepest_r,
        "delta_r": delta_r,
        "drop_per_stage": drop_per_stage,
        "monotonicity_fraction": monotonicity_fraction,
        "n_stages": len(ordered_r),
        "stage_by_stage": list(zip(ordered_states, ordered_r)),
        "summary": (f"Universality drops from r={wake_r:.3f} (wake) to "
                    f"r={deepest_r:.3f} (deepest), Δr={delta_r:.3f}, "
                    f"{monotonicity_fraction*100:.0f}% of transitions monotone")
    }
