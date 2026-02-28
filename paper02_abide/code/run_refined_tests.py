"""
run_refined_tests.py  (v3)
===========================
Three redesigned validation tests for Paper 1.

  Test A: Three-Component Variance Analysis
  Test B: Eigenvalue Stability + RMSD Landscape
  Test C: Site-Based Replication within ABIDE

Usage:
    python run_refined_tests.py              # full run
    python run_refined_tests.py --quick      # 100 ABIDE
    python run_refined_tests.py --test A/B/C
"""

import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from modules.data_acquisition import load_abide
from modules.lausanne_loader import download_lausanne, load_lausanne
from modules.refined_tests import (
    compute_three_component_analysis,
    scan_eigenvalue_stability,
    run_site_replication,
)

BASE    = SCRIPT_DIR.parent
DATA    = BASE / "data"
RESULTS = BASE / "results" / "refined"
FIGS    = BASE / "figures" / "refined"
CACHE   = DATA / "eigenspectra_cache"

for d in [RESULTS, FIGS, CACHE]:
    d.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
})
C = {
    "pmir": "#2196F3", "degree": "#4CAF50", "residual": "#FF5722",
    "abide": "#9C27B0", "lausanne": "#FF9800", "null": "#9E9E9E",
    "dark": "#1a1a2e", "stability": "#00BCD4",
}


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────

def load_all_data(max_abide=None, verbose=True):
    print("\n" + "="*65)
    print("LOADING DATA")
    print("="*65)
    subjects = load_abide(str(DATA / "abide"), max_subjects=max_abide,
                          verbose=verbose)
    print(f"  -> {len(subjects)} ABIDE subjects loaded")
    if not subjects:
        print("\nERROR: No ABIDE data found. Run download_abide.py first.")
        sys.exit(1)
    return subjects


# ─────────────────────────────────────────────────────────────────────────────
# TEST A
# ─────────────────────────────────────────────────────────────────────────────

def run_test_a(subjects, n_cl=15, verbose=True):
    print("\n" + "="*65)
    print("TEST A: THREE-COMPONENT VARIANCE ANALYSIS")
    print("="*65)

    result = compute_three_component_analysis(
        subjects, cache_dir=str(CACHE), n_cl_samples=n_cl, verbose=verbose)
    if result is None:
        return None

    out = RESULTS / "test_a_decomposition.txt"
    with open(str(out), "w") as f:
        f.write("TEST A: Three-Component Variance Analysis\n")
        f.write("=" * 52 + "\n")
        f.write(f"N subjects:                      {result['n_subjects']}\n")
        f.write(f"CL density used:                 {result['density_used']:.0%}\n\n")
        f.write(f"Between-subject actual var:      {result['var_actual_between']:.6f}\n")
        f.write(f"Between-subject CL var:          {result['var_cl_between']:.6f}\n")
        f.write(f"  -> CL convergence (mean std):  {result['cl_convergence']:.6f}\n")
        f.write(f"Between-subject residual var:    {result['var_residual_between']:.6f}\n\n")
        f.write(f"Within-subject corr (actual~CL): r = {result['within_subject_corr']:.4f}\n")
        f.write(f"Within-subject R²:               {result['within_subject_r2']*100:.1f}%\n")
        if result['diag_correlation']:
            dc = result['diag_correlation']
            f.write(f"\nResidual vs diagnosis: r={dc['r']:.4f}, p={dc['p']:.4e}, n={dc['n']}\n")
        f.write(f"\nINTERPRETATION:\n")
        if result['cl_convergence'] < 0.01:
            f.write("  CL spectra converge to a universal archetype (low between-CL var).\n")
            f.write("  Universality is enforced by shared degree-constraint, not individual degrees.\n")
        f.write(f"  Degree sequence explains {result['within_subject_r2']*100:.0f}% of")
        f.write(f" per-subject spectral variance (within-subject R²).\n")

    np.save(str(RESULTS / "test_a_actual_curves.npy"), result["actual_curves"])
    np.save(str(RESULTS / "test_a_cl_curves.npy"),     result["cl_curves"])
    np.save(str(RESULTS / "test_a_residuals.npy"),      result["residuals"])
    print(f"  Saved: {out}")

    _figure_a(result)
    return result


def _figure_a(result):
    q = np.linspace(0, 1, 200)
    A_mat = result["actual_curves"]
    D_mat = result["cl_curves"]
    R_mat = result["residuals"]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

    # Panel 1: Actual vs CL shape curves
    ax = axes[0]
    ax.fill_between(q, A_mat.mean(0)-A_mat.std(0), A_mat.mean(0)+A_mat.std(0),
                    alpha=0.2, color=C["pmir"])
    ax.fill_between(q, D_mat.mean(0)-D_mat.std(0), D_mat.mean(0)+D_mat.std(0),
                    alpha=0.2, color=C["degree"])
    ax.plot(q, A_mat.mean(0), color=C["pmir"],   lw=2, label="Actual (λ₂-rescaled)")
    ax.plot(q, D_mat.mean(0), color=C["degree"], lw=2, ls="--",
            label="Chung-Lu (degree-predicted)")
    ax.set_xlabel("Spectral quantile")
    ax.set_ylabel("Normalized eigenvalue")
    ax.set_title("A. Actual vs Degree-Predicted", fontweight="bold")
    ax.legend(fontsize=9)

    r2_ws = result["within_subject_r2"]
    ax.text(0.02, 0.98, f"Within-subject R² = {r2_ws*100:.0f}%",
            transform=ax.transAxes, va="top", fontsize=9, color=C["degree"],
            bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8))

    # Panel 2: Cross-subject variance by component
    ax = axes[1]
    ax.plot(q, A_mat.std(0),  lw=2, color=C["pmir"],    label="Actual between-subj std")
    ax.plot(q, D_mat.std(0),  lw=2, color=C["degree"],  ls="--",
            label="CL between-subj std")
    ax.fill_between(q, 0, R_mat.std(0), alpha=0.3, color=C["residual"],
                    label="Residual (higher-order)")
    ax.set_xlabel("Spectral quantile")
    ax.set_ylabel("Cross-subject std")
    ax.set_title("B. Variance Decomposition", fontweight="bold")
    ax.legend(fontsize=9)

    cl_c = result["cl_convergence"]
    ax.text(0.98, 0.98, f"CL convergence:\n{cl_c:.5f}",
            transform=ax.transAxes, ha="right", va="top", fontsize=9,
            color=C["degree"],
            bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8))

    # Panel 3: Residual magnitude distribution + diagnosis
    ax = axes[2]
    rm = result["residual_magnitudes"]
    dx = result["diagnosis_labels"]
    asd_rm  = [rm[i] for i, d in enumerate(dx) if d == 1]
    ctrl_rm = [rm[i] for i, d in enumerate(dx) if d == 2]

    if asd_rm and ctrl_rm:
        ax.hist(asd_rm,  bins=20, alpha=0.6, color=C["residual"],
                label=f"ASD (n={len(asd_rm)})", density=True)
        ax.hist(ctrl_rm, bins=20, alpha=0.6, color=C["pmir"],
                label=f"Control (n={len(ctrl_rm)})", density=True)
        ax.set_xlabel("Residual magnitude (higher-order structure)")
        ax.set_ylabel("Density")
        if result["diag_correlation"]:
            dc = result["diag_correlation"]
            p_str = f"p={dc['p']:.3f}" if dc['p'] > 0.001 else "p<0.001"
            sig = "★" if dc['p'] < 0.05 else ""
            ax.text(0.98, 0.98, f"Spearman r={dc['r']:.3f}\n{p_str} {sig}",
                    transform=ax.transAxes, ha="right", va="top", fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.9))
    else:
        ax.hist(rm, bins=25, color=C["pmir"], alpha=0.7, density=True)
        ax.set_xlabel("Residual magnitude")
        ax.set_ylabel("Density")

    ax.set_title("C. Higher-Order Structure by Diagnosis", fontweight="bold")
    ax.legend(fontsize=9)

    plt.suptitle("Three-Component Spectral Variance Analysis",
                 fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    _save_fig(fig, "Figure_TestA_Decomposition")


# ─────────────────────────────────────────────────────────────────────────────
# TEST B
# ─────────────────────────────────────────────────────────────────────────────

def run_test_b(subjects, n_sample=100, verbose=True):
    print("\n" + "="*65)
    print("TEST B: EIGENVALUE STABILITY + RMSD LANDSCAPE")
    print("="*65)

    result = scan_eigenvalue_stability(
        subjects, cache_dir=str(CACHE), n_subjects_sample=n_sample, verbose=verbose)
    if result is None:
        return None

    out = RESULTS / "test_b_landscape.txt"
    with open(str(out), "w") as f:
        f.write("TEST B: Eigenvalue Stability + RMSD Landscape\n")
        f.write("=" * 52 + "\n")
        f.write(f"N subjects scanned:     {result['n_subjects_scanned']}\n")
        f.write(f"Max rank scanned:       {result['max_rank_scanned']}\n\n")
        f.write(f"[B1: Raw Eigenvalue Stability]\n")
        f.write(f"Lambda2 (k=1) CV:       {result['lambda2_stability_cv']:.4f}\n")
        f.write(f"Most stable rank:       k = {result['best_stability_rank']}\n\n")
        f.write(f"[B2: RMSD Landscape]\n")
        f.write(f"Lambda2 (k=1) RMSD:    {result['lambda2_rmsd']:.6f}\n")
        f.write(f"Minimum RMSD at rank:  k = {result['best_rmsd_rank']}\n")
        f.write(f"Minimum RMSD:          {result['minimum_rmsd']:.6f}\n")
        f.write(f"Lambda2 is minimum:    {result['is_lambda2_rmsd_minimum']}\n\n")
        f.write("Named candidate RMSD:\n")
        for name, v in sorted(result["named_rmsd"].items(), key=lambda x: x[1]):
            f.write(f"  {name:<22} {v:.6f}\n")

    np.save(str(RESULTS / "test_b_stability_cv.npy"),  result["stability_cv"])
    np.save(str(RESULTS / "test_b_rmsd_scores.npy"),   result["rmsd_scores"])
    print(f"  Saved: {out}")

    _figure_b(result)
    return result


def _figure_b(result):
    ranks = np.arange(1, result["max_rank_scanned"] + 1)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

    # Panel 1: B1 — Raw eigenvalue CV by rank
    ax = axes[0]
    cv = result["stability_cv"]
    ax.plot(ranks, cv, color=C["dark"], lw=1.8)
    ax.scatter([1], [cv[0]], color=C["pmir"], s=120, zorder=5,
               edgecolors="white", lw=1.5, label=f"λ₂ CV={cv[0]:.3f}")
    br = result["best_stability_rank"]
    ax.scatter([br], [cv[br-1]], color=C["stability"], s=120, marker="*",
               zorder=5, edgecolors="white", lw=1.5,
               label=f"Most stable k={br}: CV={cv[br-1]:.3f}")
    ax.set_xlabel("Eigenvalue rank k")
    ax.set_ylabel("CV(λₖ) across subjects")
    ax.set_title("A. Raw Eigenvalue Stability", fontweight="bold")
    ax.legend(fontsize=9)

    # Panel 2: B2 — RMSD landscape
    ax = axes[1]
    rmsd = result["rmsd_scores"]
    ax.plot(ranks, rmsd, color=C["dark"], lw=1.8)
    ax.scatter([1], [rmsd[0]], color=C["pmir"], s=120, zorder=5,
               edgecolors="white", lw=1.5, label=f"λ₂ RMSD={rmsd[0]:.4f}")
    bk = result["best_rmsd_rank"]
    ax.scatter([bk], [result["minimum_rmsd"]], color=C["residual"],
               s=120, marker="*", zorder=5, edgecolors="white", lw=1.5,
               label=f"Min k={bk}: RMSD={result['minimum_rmsd']:.4f}")
    ax.set_xlabel("Rescaling eigenvalue rank k")
    ax.set_ylabel("RMSD from grand-mean curve")
    ax.set_title("B. RMSD Landscape", fontweight="bold")
    ax.legend(fontsize=9)
    if result["is_lambda2_rmsd_minimum"]:
        ax.text(0.5, 0.95, "λ₂ = unique minimum", transform=ax.transAxes,
                ha="center", va="top", fontsize=10, color=C["pmir"],
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", fc="#E3F2FD", alpha=0.9))

    # Panel 3: Named candidates bar
    ax = axes[2]
    items = sorted(result["named_rmsd"].items(), key=lambda x: x[1])
    names = [n for n, _ in items]
    vals  = [v for _, v in items]
    colors = [C["pmir"] if n == "lambda_2" else C["null"] for n in names]
    ax.barh(names, vals, color=colors, edgecolor="white", height=0.65)
    for i, (n, v) in enumerate(items):
        w = "bold" if n == "lambda_2" else "normal"
        col = C["pmir"] if n == "lambda_2" else "#555"
        ax.text(v + max(vals)*0.01, i, f"{v:.5f}", va="center",
                fontsize=8, color=col, fontweight=w)
    ax.set_xlabel("RMSD from grand-mean curve")
    ax.set_title("C. Named Candidate RMSD", fontweight="bold")

    plt.suptitle("λ₂ Mechanistic Validation: Stability and RMSD Landscape",
                 fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    _save_fig(fig, "Figure_TestB_Landscape")


# ─────────────────────────────────────────────────────────────────────────────
# TEST C
# ─────────────────────────────────────────────────────────────────────────────

def run_test_c(subjects, verbose=True):
    print("\n" + "="*65)
    print("TEST C: SITE-BASED REPLICATION WITHIN ABIDE")
    print("="*65)

    result = run_site_replication(
        subjects, cache_dir=str(CACHE), verbose=verbose)
    if result is None:
        return None

    out = RESULTS / "test_c_replication.txt"
    pri = result["primary"]
    sec = result["secondary"]
    with open(str(out), "w") as f:
        f.write(f"TEST C: {result['replication_type'].title()}-Based Replication\n")
        f.write("=" * 52 + "\n")
        f.write(f"Primary:   {result['primary_name']} (n={pri['n_subjects']})\n")
        f.write(f"Secondary: {result['secondary_name']} (n={sec['n_subjects']})\n\n")
        f.write(f"Primary mean r:    {pri['mean_correlation']:.4f}\n")
        f.write(f"Secondary mean r:  {sec['mean_correlation']:.4f}\n")
        f.write(f"Primary CV:        {pri['collapse_score']:.4f}\n")
        f.write(f"Secondary CV:      {sec['collapse_score']:.4f}\n")
        f.write(f"Combined pool CV:  {result['combined_collapse']['collapse_score']:.4f}\n\n")
        f.write("Replication checks:\n")
        for k, v in result["replication_checks"].items():
            f.write(f"  {k}: {v}\n")
    print(f"  Saved: {out}")

    _figure_c(result)
    return result


def _figure_c(result):
    pri = result["primary"]
    sec = result["secondary"]
    q = np.linspace(0, 1, 200)
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))

    # Panel 1: mean curves
    ax = axes[0]
    for label, res, color, ls in [
        (result["primary_name"],   pri, C["abide"],    "-"),
        (result["secondary_name"], sec, C["lausanne"], "--"),
    ]:
        mc = res["collapse_details"]["mean_curve"]
        sc = res["collapse_details"]["std_curve"]
        if mc is not None:
            ax.fill_between(q, mc-sc, mc+sc, alpha=0.15, color=color)
            ax.plot(q, mc, color=color, lw=2, ls=ls,
                    label=f"{label} (n={res['n_subjects']})")
    ax.set_xlabel("Spectral quantile")
    ax.set_ylabel("Normalized λ₂-rescaled eigenvalue")
    ax.set_title("A. Replication: Mean Shape Curves", fontweight="bold")
    ax.legend(fontsize=9)

    # Panel 2: band comparison
    ax = axes[1]
    bands = [1, 2, 3, 4, 5]
    pb = [pri["collapse_details"]["band_scores"].get(b, np.nan) for b in bands]
    sb = [sec["collapse_details"]["band_scores"].get(b, np.nan) for b in bands]
    x = np.arange(len(bands))
    ax.bar(x-0.18, pb, 0.36, color=C["abide"],    label=result["primary_name"],
           edgecolor="white")
    ax.bar(x+0.18, sb, 0.36, color=C["lausanne"], label=result["secondary_name"],
           edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels([f"Band {b}" for b in bands])
    ax.set_ylabel("Collapse CV")
    ax.set_title("B. Band-by-Band Consistency", fontweight="bold")
    ax.legend(fontsize=9)

    # Panel 3: scorecard
    ax = axes[2]
    checks = result["replication_checks"]
    labels_map = {
        "both_r_above_095": "Both r > 0.95",
        "cv_consistent":    "CV consistent",
        "combined_ok":      "Combined CV < 0.25",
    }
    labels = [labels_map.get(k, k) for k in checks.keys()]
    vals   = [int(v) for v in checks.values()]
    colors = [C["degree"] if v else C["residual"] for v in vals]
    ax.barh(labels, [1]*len(vals), color=colors, edgecolor="white", height=0.5)
    for i, v in enumerate(vals):
        ax.text(0.5, i, "PASS" if v else "FAIL", va="center", ha="center",
                fontsize=11, color="white", fontweight="bold")
    ax.set_xlim(0, 1); ax.set_xticks([])
    n_pass = sum(vals)
    ax.set_title(f"C. Replication Checks ({n_pass}/3 passed)", fontweight="bold")

    plt.suptitle(f"Cross-{result['replication_type'].title()} Replication of Spectral Universality",
                 fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    _save_fig(fig, "Figure_TestC_Replication")


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY FIGURE
# ─────────────────────────────────────────────────────────────────────────────

def make_summary_figure(res_a, res_b, res_c):
    if not all([res_a, res_b, res_c]):
        print("[SUMMARY] Skipping — one or more tests missing")
        return

    fig = plt.figure(figsize=(16, 11))
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.38)
    q  = np.linspace(0, 1, 200)

    # A1: Actual vs CL curves
    ax = fig.add_subplot(gs[0, 0])
    A_mat = res_a["actual_curves"]
    D_mat = res_a["cl_curves"]
    ax.fill_between(q, A_mat.mean(0)-A_mat.std(0), A_mat.mean(0)+A_mat.std(0),
                    alpha=0.2, color=C["pmir"])
    ax.plot(q, A_mat.mean(0), color=C["pmir"],   lw=2, label="Actual")
    ax.plot(q, D_mat.mean(0), color=C["degree"], lw=2, ls="--",
            label=f"CL (R²={res_a['within_subject_r2']*100:.0f}%/subj)")
    ax.set_title("A. Degree vs Actual", fontweight="bold")
    ax.set_xlabel("Spectral quantile"); ax.legend(fontsize=8)

    # A2: CL convergence
    ax = fig.add_subplot(gs[0, 1])
    ax.plot(q, D_mat.std(0), color=C["degree"], lw=2,
            label=f"CL between-subj std")
    ax.plot(q, A_mat.std(0), color=C["pmir"],   lw=2, ls="--",
            label="Actual between-subj std")
    ax.fill_between(q, 0, D_mat.std(0), alpha=0.3, color=C["degree"])
    ax.set_title("B. CL Convergence to Archetype", fontweight="bold")
    ax.set_xlabel("Spectral quantile"); ax.set_ylabel("Between-subject std")
    ax.text(0.98, 0.98, f"CL spread: {res_a['cl_convergence']:.5f}",
            transform=ax.transAxes, ha="right", va="top", fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.9))
    ax.legend(fontsize=8)

    # B1: Stability profile
    ax = fig.add_subplot(gs[0, 2])
    cv = res_b["stability_cv"]
    ranks = np.arange(1, len(cv)+1)
    ax.plot(ranks, cv, color=C["dark"], lw=1.5)
    ax.scatter([1], [cv[0]], color=C["pmir"], s=100, zorder=5,
               label=f"λ₂: CV={cv[0]:.3f}")
    ax.set_title("C. Eigenvalue Stability Profile", fontweight="bold")
    ax.set_xlabel("Rank k"); ax.set_ylabel("CV(λₖ)"); ax.legend(fontsize=8)

    # B2: RMSD landscape
    ax = fig.add_subplot(gs[1, 0])
    rmsd = res_b["rmsd_scores"]
    ax.plot(ranks[:len(rmsd)], rmsd, color=C["dark"], lw=1.5)
    ax.scatter([1], [rmsd[0]], color=C["pmir"], s=100, zorder=5,
               label=f"λ₂: RMSD={rmsd[0]:.4f}")
    bk = res_b["best_rmsd_rank"]
    ax.scatter([bk], [res_b["minimum_rmsd"]], color=C["residual"],
               s=100, marker="*", zorder=5,
               label=f"Min k={bk}: {res_b['minimum_rmsd']:.4f}")
    ax.set_title("D. RMSD Landscape", fontweight="bold")
    ax.set_xlabel("Rank k"); ax.set_ylabel("RMSD"); ax.legend(fontsize=8)

    # C1: Replication curves
    ax = fig.add_subplot(gs[1, 1])
    for label, res_sub, color, ls in [
        (res_c["primary_name"],   res_c["primary"],   C["abide"],    "-"),
        (res_c["secondary_name"], res_c["secondary"], C["lausanne"], "--"),
    ]:
        mc = res_sub["collapse_details"]["mean_curve"]
        if mc is not None:
            ax.plot(q, mc, color=color, lw=2, ls=ls,
                    label=f"{label} r={res_sub['mean_correlation']:.4f}")
    ax.set_title("E. Cross-Site Replication", fontweight="bold")
    ax.set_xlabel("Spectral quantile"); ax.legend(fontsize=8)

    # C2: replication scorecard
    ax = fig.add_subplot(gs[1, 2])
    checks = res_c["replication_checks"]
    labels_map = {
        "both_r_above_095": "Both r > 0.95",
        "cv_consistent":    "CV consistent",
        "combined_ok":      "Combined CV < 0.25",
    }
    labels = [labels_map.get(k, k) for k in checks]
    vals   = [int(v) for v in checks.values()]
    ax.barh(labels, [1]*len(vals),
            color=[C["degree"] if v else C["residual"] for v in vals],
            edgecolor="white", height=0.5)
    for i, v in enumerate(vals):
        ax.text(0.5, i, "PASS" if v else "FAIL", va="center", ha="center",
                fontsize=10, color="white", fontweight="bold")
    ax.set_xlim(0, 1); ax.set_xticks([])
    n_pass = sum(vals)
    ax.set_title(f"F. Replication ({n_pass}/3 passed)", fontweight="bold")

    fig.suptitle("Paper 1 Refined Validation (v3) — All Tests",
                 fontsize=14, fontweight="bold", y=1.01)
    _save_fig(fig, "Figure_AllTests_Summary")


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _save_fig(fig, stem):
    for ext in ["pdf", "png"]:
        p = FIGS / f"{stem}.{ext}"
        fig.savefig(str(p))
        print(f"  Figure saved: {p}")
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-abide", type=int, default=None)
    parser.add_argument("--test", choices=["A", "B", "C", "all"], default="all")
    parser.add_argument("--quick", action="store_true",
                        help="Limit to 100 ABIDE subjects")
    args = parser.parse_args()

    if args.quick:
        args.max_abide = args.max_abide or 100
        print(f"[QUICK MODE] max_abide={args.max_abide}")

    subjects = load_all_data(max_abide=args.max_abide)

    n_cl   = 5  if args.quick else 15
    n_samp = 50 if args.quick else 200

    res_a, res_b, res_c = None, None, None

    if args.test in ("A", "all"):
        res_a = run_test_a(subjects, n_cl=n_cl)

    if args.test in ("B", "all"):
        res_b = run_test_b(subjects, n_sample=n_samp)

    if args.test in ("C", "all"):
        res_c = run_test_c(subjects)

    if args.test == "all":
        make_summary_figure(res_a, res_b, res_c)

    print("\n" + "="*65)
    print("DONE")
    print(f"  Results: {RESULTS}")
    print(f"  Figures: {FIGS}")
    print("="*65)
