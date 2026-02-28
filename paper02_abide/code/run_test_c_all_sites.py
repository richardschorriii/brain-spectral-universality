"""
run_test_c_all_sites.py
=======================
Run Test C spectral universality analysis across ALL viable ABIDE sites
(not just the top two). Outputs a CSV table with r and CV for every site,
plus a figure ready for the manuscript.

Usage:
    python run_test_c_all_sites.py

Output:
    results/refined/test_c_all_sites.csv
    figures/refined/Figure_TestC_AllSites.pdf / .png
"""

import sys
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from modules.data_acquisition import load_abide
from modules.spectral_analysis import compute_spectral_universality

BASE    = SCRIPT_DIR.parent
DATA    = BASE / "data"
RESULTS = BASE / "results" / "refined"
FIGS    = BASE / "figures" / "refined"
CACHE   = DATA / "eigenspectra_cache"

for d in [RESULTS, FIGS]:
    d.mkdir(parents=True, exist_ok=True)

MIN_SUBJECTS = 10   # minimum per site to run analysis


def main():
    # ── Load all subjects ────────────────────────────────────────────────────
    print("Loading ABIDE subjects...")
    subjects = load_abide(str(DATA / "abide"), verbose=True)
    print(f"  Loaded: {len(subjects)} subjects\n")

    # ── Group by site ────────────────────────────────────────────────────────
    sites = {}
    for s in subjects:
        site = s.get("metadata", {}).get("site", "Unknown")
        sites.setdefault(site, []).append(s)

    print(f"Sites found: {len(sites)}")
    for site, subs in sorted(sites.items(), key=lambda x: -len(x[1])):
        viable = "viable" if len(subs) >= MIN_SUBJECTS else "skip"
        print(f"  {site:<12} n={len(subs):<5} [{viable}]")

    # ── Run per-site analysis ────────────────────────────────────────────────
    print(f"\nRunning spectral universality for each site (min n={MIN_SUBJECTS})...")
    print(f"{'Site':<14} {'N':>5}  {'Mean r':>8}  {'CV':>8}  {'λ₂ mean':>10}  {'λ₂ CV%':>8}")
    print("-" * 65)

    rows = []
    for site, subs in sorted(sites.items(), key=lambda x: -len(x[1])):
        if len(subs) < MIN_SUBJECTS:
            print(f"  {site:<14} n={len(subs):<3}  [SKIPPED — too few subjects]")
            continue

        result = compute_spectral_universality(
            subs, "lambda2", cache_dir=str(CACHE), verbose=False
        )

        if result is None:
            print(f"  {site:<14} n={len(subs):<3}  [FAILED]")
            continue

        r       = result["mean_correlation"]
        cv      = result["collapse_score"]
        # lambda2 values are returned directly in result
        l2_vals = result["lambda2_values"]
        l2_mean = float(np.mean(l2_vals))
        l2_cv   = float(np.std(l2_vals) / l2_mean * 100) if l2_mean > 0 else np.nan

        # Count diagnosis
        n_asd  = sum(1 for s in subs if s.get("metadata", {}).get("diagnosis") == 1)
        n_ctrl = sum(1 for s in subs if s.get("metadata", {}).get("diagnosis") == 2)

        print(f"  {site:<14} {len(subs):>5}  {r:>8.4f}  {cv:>8.4f}  "
              f"{l2_mean:>10.4f}  {l2_cv:>7.1f}%")

        rows.append({
            "site":      site,
            "n":         len(subs),
            "mean_r":    round(r, 4),
            "cv":        round(cv, 4),
            "l2_mean":   round(l2_mean, 4) if not np.isnan(l2_mean) else "",
            "l2_cv_pct": round(l2_cv, 1)   if not np.isnan(l2_cv)  else "",
            "n_asd":     n_asd,
            "n_ctrl":    n_ctrl,
            "rmsd":      round(result.get("mean_rmsd", np.nan), 4),
        })

    if not rows:
        print("\nNo sites had enough subjects. Check MIN_SUBJECTS threshold.")
        return

    # ── Save CSV ─────────────────────────────────────────────────────────────
    csv_path = RESULTS / "test_c_all_sites.csv"
    fields = ["site", "n", "mean_r", "cv", "l2_mean", "l2_cv_pct",
              "n_asd", "n_ctrl", "rmsd"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved: {csv_path}")

    # ── Figure ───────────────────────────────────────────────────────────────
    _make_figure(rows)


def _make_figure(rows):
    # Sort by n descending
    rows = sorted(rows, key=lambda x: -x["n"])

    sites  = [r["site"] for r in rows]
    ns     = [r["n"] for r in rows]
    rs     = [r["mean_r"] for r in rows]
    cvs    = [r["cv"] for r in rows]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    plt.rcParams.update({'font.family': 'serif', 'font.size': 10,
                          'axes.spines.top': False, 'axes.spines.right': False})

    BLUE = '#2E5494'
    RED  = '#C0392B'

    cmap = plt.cm.Blues
    norm_n = plt.Normalize(min(ns), max(ns))

    # ── Left: r by site (bubble = n) ────────────────────────────────────────
    ax = axes[0]
    scatter_colors = [cmap(norm_n(n)) for n in ns]
    for i, (site, n, r) in enumerate(zip(sites, ns, rs)):
        ax.scatter(i, r, s=n * 1.2, color=scatter_colors[i],
                   edgecolors=BLUE, lw=0.8, zorder=4, alpha=0.85)
    ax.axhline(0.95, color=RED, ls='--', lw=1.2, label='Threshold r = 0.95')
    ax.axhline(np.mean(rs), color=BLUE, ls=':', lw=1.2, alpha=0.7,
               label=f'Grand mean r = {np.mean(rs):.4f}')
    ax.set_xticks(range(len(sites)))
    ax.set_xticklabels(sites, rotation=50, ha='right', fontsize=8.5)
    ax.set_ylim(min(rs) - 0.01, 1.0)
    ax.set_ylabel("Mean inter-subject correlation (r)")
    ax.set_title("A  Spectral universality by acquisition site\n(bubble size = n)",
                 loc='left', fontweight='bold', fontsize=10)
    ax.legend(fontsize=8.5, loc='lower right')
    ax.grid(axis='y', alpha=0.25, zorder=1)

    # Annotate n for each site
    for i, (n, r) in enumerate(zip(ns, rs)):
        ax.text(i, r + 0.001, f'n={n}', ha='center', va='bottom',
                fontsize=6.5, color='#333')

    # ── Right: CV by site ────────────────────────────────────────────────────
    ax2 = axes[1]
    bar_colors = [BLUE if cv < 0.20 else ('#E67E22' if cv < 0.25 else RED) for cv in cvs]
    bars = ax2.bar(range(len(sites)), cvs, color=bar_colors, alpha=0.85,
                   edgecolor='white', lw=1, zorder=3)
    ax2.axhline(0.25, color=RED, ls='--', lw=1.2, label='Threshold CV = 0.25')
    ax2.axhline(np.mean(cvs), color=BLUE, ls=':', lw=1.2, alpha=0.7,
                label=f'Grand mean CV = {np.mean(cvs):.4f}')
    ax2.set_xticks(range(len(sites)))
    ax2.set_xticklabels(sites, rotation=50, ha='right', fontsize=8.5)
    ax2.set_ylabel("Collapse score (CV — lower is better)")
    ax2.set_title("B  Collapse consistency by site",
                  loc='left', fontweight='bold', fontsize=10)
    ax2.legend(fontsize=8.5)
    ax2.grid(axis='y', alpha=0.25, zorder=1)

    # Legend for bar colors
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=BLUE,      label='CV < 0.20 (excellent)'),
        Patch(facecolor='#E67E22', label='0.20 ≤ CV < 0.25 (good)'),
        Patch(facecolor=RED,       label='CV ≥ 0.25 (poor)'),
    ]
    ax2.legend(handles=legend_elements, fontsize=8, loc='upper right')

    n_pass = sum(1 for r in rs if r > 0.95)
    fig.suptitle(
        f"Test C — All-Site Spectral Universality (ABIDE, {len(rows)} sites, "
        f"{sum(ns)} subjects total)\n{n_pass}/{len(rows)} sites r > 0.95",
        fontsize=11, fontweight='bold'
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])

    for ext in ['pdf', 'png']:
        path = FIGS / f"Figure_TestC_AllSites.{ext}"
        fig.savefig(str(path), dpi=300)
        print(f"Figure saved: {path}")
    plt.close()


if __name__ == "__main__":
    main()
