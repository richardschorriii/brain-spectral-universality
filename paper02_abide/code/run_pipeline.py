"""
PAPER 1: Main Pipeline Orchestrator
Runs all stages of the analysis in order, following the research plan exactly.

SEQUENCE:
  Stage 0: Setup and data download instructions
  Stage 1: Load all datasets
  Stage 2: Primary spectral universality test (resting state, lambda2 rescaling)
  Stage 3: Rescaling comparison (lambda2 vs lambda_max vs mean)
  Stage 4: Null model evaluation (all 4 types)
  Stage 5: Permutation test for statistical significance
  Stage 6: Parcellation independence test
  Stage 7: Consciousness gradient analysis
  Stage 8: Confirmation/falsification verdict
  Stage 9: Save all results for paper

Run with: python run_pipeline.py
Or run individual stages by importing from this module.
"""

import os
import sys
import json
import pickle
import numpy as np
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from modules.data_acquisition import load_all_datasets
from modules.spectral_analysis import (
    compute_spectral_universality, compare_rescaling_methods
)
from modules.null_models import run_all_null_models, permutation_test
from modules.consciousness_analysis import (
    analyze_consciousness_gradient, test_parcellation_independence,
    quantify_universality_drop
)

TICK = "OK"
CROSS = "XX"


def _fmt(passed):
    return "[OK]" if passed else "[XX]"


# =============================================================================
# STAGE 0: SETUP
# =============================================================================

def stage_0_setup():
    """Create directories, check dependencies, print data download instructions."""
    print("=" * 70)
    print("PAPER 1: Consciousness-State Spectral Universality")
    print("PMIR Prediction: rho(lambda/lambda2) is universal across subjects and states")
    print("=" * 70)

    for d in [config.DATA_DIR, config.RESULTS_DIR, config.FIGURES_DIR,
              config.NULL_MODELS_DIR, config.COMPUTE["cache_dir"]]:
        os.makedirs(d, exist_ok=True)

    required = ["numpy", "scipy", "nilearn", "networkx", "matplotlib", "pandas"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"\n[WARN] Missing packages: {missing}")
        print(f"Install with: pip install {' '.join(missing)}")
    else:
        print("\n[OK] All required packages available")

    print("\n--- DATA DOWNLOAD INSTRUCTIONS ---")
    print("\n1. RAJ LAB HCP (primary, N=1071):")
    print("   git clone https://github.com/Raj-Lab-UCSF/spectrome")
    print(f"   cp -r spectrome/data/hcp/* {config.DATASETS['raj_lab_hcp']['data_path']}/")
    print("\n2. ABIDE (via nilearn, automatic):")
    print("   Will auto-download when pipeline runs. Requires ~2GB disk space.")
    print("\n3. OpenNeuro sleep dataset (ds003768):")
    print("   pip install openneuro-py")
    print(f"   openneuro download ds003768 {config.DATASETS['openneuro_sleep']['data_path']}")
    print("   OR: aws s3 sync s3://openneuro.org/ds003768 <path> --no-sign-request")
    print("\n4. OpenNeuro propofol dataset:")
    print("   Search openneuro.org for propofol fMRI dataset")
    print(f"   Download to: {config.DATASETS['openneuro_propofol']['data_path']}")
    print("\n--- To run pipeline after data download: python run_pipeline.py ---\n")


# =============================================================================
# STAGE 1: LOAD DATA
# =============================================================================

def stage_1_load_data():
    """Load all enabled datasets. Returns flat list of subject dicts."""
    print("\n" + "=" * 50)
    print("STAGE 1: Loading datasets")
    print("=" * 50)
    subjects = load_all_datasets(config)
    print(f"\n[OK] Stage 1 complete: {len(subjects)} subject-state pairs loaded")
    return subjects


# =============================================================================
# STAGE 2: PRIMARY UNIVERSALITY TEST
# =============================================================================

def stage_2_primary_test(subjects):
    """
    Primary test: inter-subject spectral correlation in resting state.
    Goal: r > 0.95 with lambda2 rescaling.
    """
    print("\n" + "=" * 50)
    print("STAGE 2: Primary Universality Test (lambda2 rescaling, resting state)")
    print("=" * 50)

    rest_subjects = [s for s in subjects if s.get("state", "").lower() in
                     ("rest", "wake", "awake", "resting")]
    print(f"Resting state subjects: {len(rest_subjects)}")

    if len(rest_subjects) < 5:
        print("[WARN] Too few resting-state subjects. Check data loading.")
        return None

    result = compute_spectral_universality(
        rest_subjects,
        rescaling_method="lambda2",
        laplacian_type=config.LAPLACIAN["type"],
        cache_dir=config.COMPUTE["cache_dir"] if config.COMPUTE["cache_eigenspectra"] else None,
        verbose=True,
    )

    if result:
        r = result["mean_correlation"]
        threshold = config.THRESHOLDS["min_correlation_resting"]
        status = "[OK] CONFIRMED" if r > threshold else f"[XX] BELOW THRESHOLD ({threshold})"
        print(f"\n[STAGE 2] r = {r:.4f} | Target: >{threshold} | {status}")

    return result


# =============================================================================
# STAGE 3: RESCALING COMPARISON
# =============================================================================

def stage_3_rescaling_comparison(subjects):
    """
    Compare lambda2 rescaling against alternatives. lambda2 should be privileged.
    Uses collapse score (mean CV), not Pearson r, as the discriminating metric.
    """
    print("\n" + "=" * 50)
    print("STAGE 3: Rescaling Method Comparison")
    print("=" * 50)

    rest_subjects = [s for s in subjects if s.get("state", "").lower() in
                     ("rest", "wake", "awake", "resting")]

    methods = [k for k, v in config.RESCALING_METHODS.items() if v.get("enabled")]
    results = compare_rescaling_methods(
        rest_subjects,
        methods=methods,
        laplacian_type=config.LAPLACIAN["type"],
        cache_dir=config.COMPUTE["cache_dir"] if config.COMPUTE["cache_eigenspectra"] else None,
    )
    return results


# =============================================================================
# STAGE 4: NULL MODELS
# =============================================================================

def stage_4_null_models(subjects, primary_result):
    """Run all null model types and compare against observed universality."""
    print("\n" + "=" * 50)
    print("STAGE 4: Null Model Evaluation")
    print("=" * 50)

    rest_subjects = [s for s in subjects if s.get("state", "").lower() in
                     ("rest", "wake", "awake", "resting")]

    observed_r = primary_result["mean_correlation"] if primary_result else None
    real_rmsd   = primary_result.get("mean_rmsd")   if primary_result else None

    results = run_all_null_models(
        rest_subjects,
        observed_r=observed_r,
        rescaling_method="lambda2",
        config=config,
        verbose=True,
        real_rmsd=real_rmsd,
    )
    return results


# =============================================================================
# STAGE 5: PERMUTATION TEST
# =============================================================================

def stage_5_permutation_test(primary_result):
    """Permutation test for statistical significance."""
    print("\n" + "=" * 50)
    print("STAGE 5: Permutation Test")
    print("=" * 50)

    if primary_result is None:
        print("[WARN] No primary result available, skipping permutation test")
        return None

    p_value, perm_corrs, observed_r = permutation_test(
        primary_result["rescaled_spectra"],
        n_permutations=config.STATISTICS["permutation_test_n"],
        observed_r=primary_result["mean_correlation"],
        verbose=True,
    )

    sig = p_value < config.STATISTICS["significance_threshold"]
    thresh = config.STATISTICS["significance_threshold"]
    print(f"[STAGE 5] p={p_value:.2e} | Significant (p<{thresh}): {_fmt(sig)}")

    return {"p_value": p_value, "permuted_correlations": perm_corrs,
            "observed_r": observed_r, "significant": sig}


# =============================================================================
# STAGE 6: PARCELLATION INDEPENDENCE
# =============================================================================

def stage_6_parcellation_test(subjects_by_parcellation):
    """Test that universality holds across 3+ parcellation schemes."""
    print("\n" + "=" * 50)
    print("STAGE 6: Parcellation Independence Test")
    print("=" * 50)

    parc_results, consistency = test_parcellation_independence(
        subjects_by_parcellation,
        rescaling_method="lambda2",
        cache_dir=config.COMPUTE["cache_dir"] if config.COMPUTE["cache_eigenspectra"] else None,
        verbose=True,
    )

    threshold = config.THRESHOLDS["min_parcellations_confirmed"]
    n_confirmed = consistency["n_above_0.95"]
    status = "[OK] CONFIRMED" if n_confirmed >= threshold else f"[XX] Only {n_confirmed}/{threshold} confirmed"
    print(f"\n[STAGE 6] {n_confirmed} parcellations with r>0.95 | Need {threshold} | {status}")

    return parc_results, consistency


# =============================================================================
# STAGE 7: CONSCIOUSNESS GRADIENT
# =============================================================================

def stage_7_consciousness_gradient(subjects):
    """Test systematic universality degradation with consciousness loss."""
    print("\n" + "=" * 50)
    print("STAGE 7: Consciousness State Gradient")
    print("=" * 50)

    state_results, gradient_test = analyze_consciousness_gradient(
        subjects,
        rescaling_method="lambda2",
        cache_dir=config.COMPUTE["cache_dir"] if config.COMPUTE["cache_eigenspectra"] else None,
        verbose=True,
    )

    drop_stats = quantify_universality_drop(gradient_test)
    if drop_stats:
        print(f"\n[STAGE 7] {drop_stats['summary']}")

    return state_results, gradient_test, drop_stats


# =============================================================================
# STAGE 8: VERDICT
# =============================================================================

def stage_8_verdict(primary_result, null_results, permutation_result,
                    rescaling_comparison, parcellation_consistency,
                    gradient_test, drop_stats):
    """
    Apply confirmation/falsification criteria from research plan.
    Returns structured verdict dict.
    """
    print("\n" + "=" * 70)
    print("STAGE 8: CONFIRMATION / FALSIFICATION VERDICT")
    print("=" * 70)

    verdict = {
        "timestamp": datetime.now().isoformat(),
        "checks": {},
        "overall": None,
        "notes": [],
    }

    # ------------------------------------------------------------------
    # Check 1: r > 0.95 resting state
    # ------------------------------------------------------------------
    if primary_result:
        r = primary_result["mean_correlation"]
        check1 = r > config.THRESHOLDS["min_correlation_resting"]
        verdict["checks"]["resting_r_above_095"] = {
            "result": check1,
            "value": r,
            "threshold": config.THRESHOLDS["min_correlation_resting"],
        }
        print(f"{_fmt(check1)} Resting r={r:.4f} > 0.95: {check1}")

    # ------------------------------------------------------------------
    # Check 2: Degree-preserved null falsification
    # Criterion: brain RMSD < degree-null RMSD (brain more universal)
    # ------------------------------------------------------------------
    if null_results:
        deg_res = null_results.get("degree_preserved", {})
        falsification_triggered = deg_res.get("falsification_triggered", True)
        check2 = not falsification_triggered
        real_rmsd_val = deg_res.get("real_rmsd", None)
        deg_null_rmsd = deg_res.get("null_mean", None)
        verdict["checks"]["degree_null_falsification"] = {
            "result": check2,
            "real_rmsd": real_rmsd_val,
            "degree_null_rmsd": deg_null_rmsd,
            "interpretation": "real brain RMSD < degree-null RMSD (brain more universal)",
        }
        if real_rmsd_val is not None and deg_null_rmsd is not None:
            print(f"{_fmt(check2)} Brain RMSD={real_rmsd_val:.4f} < degree-null RMSD={deg_null_rmsd:.4f}: {check2}")

        # All null models significant
        all_sig = all(
            (res.get("p_value") or 1.0) < config.STATISTICS["significance_threshold"]
            for res in null_results.values()
        )
        verdict["checks"]["null_models_significant"] = {"result": all_sig}
        print(f"{_fmt(all_sig)} All null models significant: {all_sig}")

    # ------------------------------------------------------------------
    # Check 3: lambda2 privileged over alternatives (collapse score)
    # ------------------------------------------------------------------
    if rescaling_comparison:
        lambda2_cs = rescaling_comparison.get("lambda2", {}).get("collapse_score", None)
        others_cs = {k: v["collapse_score"] for k, v in rescaling_comparison.items()
                     if k != "lambda2" and v and "collapse_score" in v}
        if lambda2_cs is not None and others_cs:
            lambda2_privileged = all(lambda2_cs <= cs + 0.001 for cs in others_cs.values())
        else:
            lambda2_privileged = None
        verdict["checks"]["lambda2_privileged"] = {
            "result": lambda2_privileged,
            "lambda2_collapse_score": lambda2_cs,
            "alternatives_collapse_scores": others_cs,
            "note": "collapse_score = mean pointwise CV; lower = tighter spectral collapse",
        }
        if lambda2_cs is not None:
            print(f"{_fmt(lambda2_privileged)} lambda2 collapse score {lambda2_cs:.4f} <= alternatives: {lambda2_privileged}")

    # ------------------------------------------------------------------
    # Check 4: Parcellation independence
    # ------------------------------------------------------------------
    if parcellation_consistency:
        n_parc = parcellation_consistency["n_above_0.95"]
        threshold = config.THRESHOLDS["min_parcellations_confirmed"]
        check4 = n_parc >= threshold and not parcellation_consistency["falsification_triggered"]
        verdict["checks"]["parcellation_independent"] = {
            "result": check4,
            "n_parcellations_above_095": n_parc,
            "threshold": threshold,
        }
        print(f"{_fmt(check4)} Parcellation independent ({n_parc}/{threshold}): {check4}")

    # ------------------------------------------------------------------
    # Check 5: Consciousness gradient
    # ------------------------------------------------------------------
    if gradient_test:
        gradient_confirmed = gradient_test["result"] == "CONFIRMED"
        verdict["checks"]["consciousness_gradient"] = {
            "result": gradient_confirmed,
            "spearman_rho": gradient_test["spearman_rho"],
            "p_value": gradient_test["p_value_one_tailed"],
        }
        if drop_stats:
            verdict["checks"]["consciousness_gradient"]["delta_r"] = drop_stats["delta_r"]
        print(f"{_fmt(gradient_confirmed)} Consciousness gradient confirmed: {gradient_confirmed}")

    # ------------------------------------------------------------------
    # Overall verdict
    # ------------------------------------------------------------------
    confirmations = sum(1 for v in verdict["checks"].values() if v.get("result"))
    total_checks = len(verdict["checks"])
    verdict["overall"] = "CONFIRMED" if confirmations == total_checks else (
        "PARTIAL" if confirmations > total_checks // 2 else "FALSIFIED"
    )
    verdict["confirmation_rate"] = f"{confirmations}/{total_checks}"

    print(f"\n{'='*50}")
    print(f"OVERALL VERDICT: {verdict['overall']} ({confirmations}/{total_checks} checks passed)")
    print(f"{'='*50}")

    return verdict


# =============================================================================
# STAGE 9: SAVE RESULTS
# =============================================================================

def stage_9_save_results(all_results, label="run"):
    """Save all results to disk in formats suitable for paper figures/tables."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(config.RESULTS_DIR, f"{label}_{timestamp}")
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, "all_results.pkl"), "wb") as f:
        pickle.dump(all_results, f)

    if "verdict" in all_results:
        def _json_safe(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, (np.bool_, np.integer)):
                return obj.item()
            if isinstance(obj, (np.floating,)):
                return float(obj)
            if isinstance(obj, dict):
                return {k: _json_safe(v) for k, v in obj.items()}
            if isinstance(obj, (list, tuple)):
                return [_json_safe(i) for i in obj]
            return obj
        with open(os.path.join(out_dir, "verdict.json"), "w") as f:
            json.dump(_json_safe(all_results["verdict"]), f, indent=2)

    print(f"\n[SAVE] Results saved to: {out_dir}")
    return out_dir


# =============================================================================
# FULL PIPELINE
# =============================================================================

def run_full_pipeline():
    """Execute all stages in order."""
    stage_0_setup()

    # Stage 1: Load data
    subjects = stage_1_load_data()
    if len(subjects) == 0:
        print("\n[WARN] No data loaded. Follow download instructions above, then re-run.")
        return

    # Stage 2: Primary test
    primary_result = stage_2_primary_test(subjects)

    # Stage 3: Rescaling comparison
    rescaling_results = stage_3_rescaling_comparison(subjects)

    # Stage 4: Null models
    null_results = stage_4_null_models(subjects, primary_result) if primary_result else None

    # Stage 5: Permutation test
    perm_result = stage_5_permutation_test(primary_result)

    # Stage 6: Parcellation independence
    from collections import defaultdict
    by_parc = defaultdict(list)
    for s in subjects:
        by_parc[s.get("parcellation", "default")].append(s)
    parc_results, parc_consistency = stage_6_parcellation_test(dict(by_parc))

    # Stage 7: Consciousness gradient
    state_results, gradient_test, drop_stats = stage_7_consciousness_gradient(subjects)

    # Stage 8: Verdict
    verdict = stage_8_verdict(
        primary_result, null_results, perm_result,
        rescaling_results, parc_consistency,
        gradient_test, drop_stats
    )

    # Stage 9: Save
    all_results = {
        "primary_result": primary_result,
        "rescaling_comparison": rescaling_results,
        "null_models": null_results,
        "permutation_test": perm_result,
        "parcellation_results": parc_results,
        "parcellation_consistency": parc_consistency,
        "state_results": state_results,
        "gradient_test": gradient_test,
        "drop_stats": drop_stats,
        "verdict": verdict,
    }
    out_dir = stage_9_save_results(all_results, label="paper1")

    return all_results, out_dir


if __name__ == "__main__":
    run_full_pipeline()
