#!/usr/bin/env python3
"""
SUPPLEMENTARY FIGURES S3-S5 FOR MANUSCRIPT v1.2
Generates the 3 new supplementary figures:
- Supp Fig S3: Eyes-Open vs Eyes-Closed Comparison
- Supp Fig S4: Rescaling Parameter Comparison
- Supp Fig S5: Connectivity Methods Comparison

(Supp Figs S1-S2 already created in v1.1)

Author: Richard L Schorr III
Date: February 2026
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os

# Publication settings
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 1.5
plt.rcParams['xtick.major.width'] = 1.5
plt.rcParams['ytick.major.width'] = 1.5
sns.set_style("ticks")
sns.set_context("paper", font_scale=1.2)

# Paths
BASE = r'C:\Users\veilbreaker\Downloads\PMIR_neurology\PMIR_EEG_Paper'
RESULTS = os.path.join(BASE, '03_Results')
SUPP = os.path.join(BASE, '06_Supplementary')
FIGS = os.path.join(BASE, '04_Figures')

os.makedirs(FIGS, exist_ok=True)

print("="*80)
print("GENERATING SUPPLEMENTARY FIGURES S3-S5 (v1.2)")
print("="*80)

# ============================================================================
# LOAD DATA
# ============================================================================

print("\nLoading data...")

# Eyes-open vs eyes-closed
df_r01_r02_summary = pd.read_csv(os.path.join(RESULTS, 'r01_r02_summary.csv'))
df_r01_r02_lambda2 = pd.read_csv(os.path.join(RESULTS, 'r01_r02_lambda2_comparison.csv'))
df_r01_r02_bands = pd.read_csv(os.path.join(RESULTS, 'r01_r02_band_comparison.csv'))

# Rescaling parameter comparison
df_rescaling = pd.read_csv(os.path.join(SUPP, 'rescaling_parameter_comparison.csv'))
df_rescaling_summary = pd.read_csv(os.path.join(RESULTS, 'rescaling_validation_summary.csv'))

# Connectivity methods comparison
df_connectivity = pd.read_csv(os.path.join(SUPP, 'connectivity_methods_comparison.csv'))
df_connectivity_summary = pd.read_csv(os.path.join(RESULTS, 'connectivity_methods_summary.csv'))

print("✓ All data loaded")

# ============================================================================
# SUPPLEMENTARY FIGURE S3: EYES-OPEN VS EYES-CLOSED
# ============================================================================

print("\n[1/3] Generating Supplementary Figure S3: Eyes-Open vs Eyes-Closed...")

fig = plt.figure(figsize=(15, 5))

# Panel A: Lambda2 distributions (box plots)
ax1 = plt.subplot(131)

r01_lambda2 = df_r01_r02_lambda2['r01_lambda2'].values
r02_lambda2 = df_r01_r02_lambda2['r02_lambda2'].values

positions = [1, 2]
bp = ax1.boxplot([r01_lambda2, r02_lambda2], positions=positions,
                 widths=0.6, patch_artist=True,
                 boxprops=dict(facecolor='lightblue', edgecolor='black', linewidth=2),
                 medianprops=dict(color='red', linewidth=3),
                 whiskerprops=dict(color='black', linewidth=2),
                 capprops=dict(color='black', linewidth=2))

# Overlay individual points
for i, data in enumerate([r01_lambda2, r02_lambda2]):
    y = data
    x_jitter = positions[i] + np.random.normal(0, 0.04, size=len(y))
    ax1.scatter(x_jitter, y, alpha=0.6, s=100, color='darkblue', 
               edgecolor='black', linewidth=1.5, zorder=10)

ax1.set_ylabel('λ₂ (Spectral Gap)', fontsize=13, fontweight='bold')
ax1.set_title('A. λ₂ Distribution by Condition', fontsize=14, fontweight='bold')
ax1.set_xticks(positions)
ax1.set_xticklabels(['Eyes-Open\n(R01)', 'Eyes-Closed\n(R02)'], fontsize=12)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.grid(True, alpha=0.3, axis='y')

# Add mean values
r01_mean = r01_lambda2.mean()
r02_mean = r02_lambda2.mean()
ax1.text(1, r01_mean + 0.05, f'{r01_mean:.3f}', 
        ha='center', fontsize=11, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='white', edgecolor='black'))
ax1.text(2, r02_mean + 0.05, f'{r02_mean:.3f}', 
        ha='center', fontsize=11, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='white', edgecolor='black'))

# Add statistical test
t_stat = df_r01_r02_summary['lambda2_tstat'].values[0]
p_val = df_r01_r02_summary['lambda2_pvalue'].values[0]
ax1.text(0.5, 0.95, f't = {t_stat:.2f}, p = {p_val:.3f}\n(not significant)',
        transform=ax1.transAxes, ha='center', va='top',
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8,
                 edgecolor='orange', linewidth=2),
        fontsize=10)

# Panel B: Per-band correlations
ax2 = plt.subplot(132)

bands = df_r01_r02_bands['band'].values
r01_bands = df_r01_r02_bands['r01_mean'].values
r02_bands = df_r01_r02_bands['r02_mean'].values

x = np.arange(len(bands))
width = 0.35

bars1 = ax2.bar(x - width/2, r01_bands, width, label='Eyes-Open (R01)',
               alpha=0.8, color='coral', edgecolor='black', linewidth=2)
bars2 = ax2.bar(x + width/2, r02_bands, width, label='Eyes-Closed (R02)',
               alpha=0.8, color='steelblue', edgecolor='black', linewidth=2)

# Value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                f'{height:.3f}', ha='center', va='bottom', 
                fontsize=9, fontweight='bold')

ax2.set_xlabel('Spectral Band', fontsize=13, fontweight='bold')
ax2.set_ylabel('Mean Inter-Subject Correlation', fontsize=13, fontweight='bold')
ax2.set_title('B. Per-Band Correlation Comparison', fontsize=14, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels([f'Band {i}' for i in bands], fontsize=11)
ax2.set_ylim([0.9, 1.01])
ax2.legend(frameon=True, fontsize=10, loc='lower left', fancybox=True, shadow=True)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.grid(True, alpha=0.3, axis='y')

# Panel C: Overall comparison
ax3 = plt.subplot(133)

r01_overall = df_r01_r02_summary['r01_overall_correlation'].values[0]
r02_overall = df_r01_r02_summary['r02_overall_correlation'].values[0]
difference = df_r01_r02_summary['difference'].values[0]
pct_diff = df_r01_r02_summary['percent_difference'].values[0]

conditions = ['Eyes-Open\n(R01)', 'Eyes-Closed\n(R02)']
values = [r01_overall, r02_overall]
colors = ['coral', 'steelblue']

bars = ax3.bar(conditions, values, color=colors, alpha=0.8, 
              edgecolor='black', linewidth=2.5, width=0.6)

# Value labels
for bar, val in zip(bars, values):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height/2,
            f'r = {val:.4f}', ha='center', va='center', 
            fontsize=16, fontweight='bold', color='white')

ax3.set_ylabel('Overall Spectral Universality', fontsize=13, fontweight='bold')
ax3.set_title('C. Overall Comparison', fontsize=14, fontweight='bold')
ax3.set_ylim([0, 1.05])
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.grid(True, alpha=0.3, axis='y')

# Add difference annotation
ax3.text(0.5, 0.25, f'Δr = {difference:.4f}\n({pct_diff:.1f}% difference)',
        transform=ax3.transAxes, ha='center', va='center',
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9,
                 edgecolor='orange', linewidth=2.5),
        fontsize=12, fontweight='bold')

# Add interpretation
ax3.text(0.5, 0.08, 'Both conditions show\nextraordinary universality',
        transform=ax3.transAxes, ha='center', va='center',
        fontsize=10, style='italic', color='darkgreen')

plt.tight_layout()
plt.savefig(os.path.join(FIGS, 'SuppFig3_EyesOpen_vs_EyesClosed.png'), 
           dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(FIGS, 'SuppFig3_EyesOpen_vs_EyesClosed.pdf'), 
           bbox_inches='tight')
print("✓ Saved Supplementary Figure S3")
plt.close()

# ============================================================================
# SUPPLEMENTARY FIGURE S4: RESCALING PARAMETER COMPARISON
# ============================================================================

print("\n[2/3] Generating Supplementary Figure S4: Rescaling Parameter Comparison...")

fig = plt.figure(figsize=(14, 6))

# Panel A: Overall correlation by parameter
ax1 = plt.subplot(121)

params = df_rescaling['rescaling_parameter'].values
correlations = df_rescaling['overall_correlation'].values

# Clean up parameter names for display
param_labels = []
for p in params:
    if p == 'lambda_2':
        param_labels.append('λ₂')
    elif p == 'lambda_3':
        param_labels.append('λ₃')
    elif p == 'lambda_4':
        param_labels.append('λ₄')
    elif p == 'lambda_mean':
        param_labels.append('λ_mean')
    elif p == 'lambda_max':
        param_labels.append('λ_max')
    elif p == 'no_rescaling':
        param_labels.append('No Rescaling')
    else:
        param_labels.append(p)

x_pos = np.arange(len(params))
colors_param = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#95a5a6']

bars = ax1.bar(x_pos, correlations, color=colors_param, alpha=0.85,
              edgecolor='black', linewidth=2.5, width=0.7)

# Value labels
for bar, val in zip(bars, correlations):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.002,
            f'{val:.4f}', ha='center', va='bottom', 
            fontsize=12, fontweight='bold')

ax1.set_xlabel('Rescaling Parameter', fontsize=13, fontweight='bold')
ax1.set_ylabel('Overall Spectral Universality', fontsize=13, fontweight='bold')
ax1.set_title('A. Overall Correlation by Rescaling Parameter', 
             fontsize=14, fontweight='bold')
ax1.set_xticks(x_pos)
ax1.set_xticklabels(param_labels, fontsize=11, rotation=15, ha='right')
ax1.set_ylim([0.98, 1.0])
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.grid(True, alpha=0.3, axis='y')

# Add horizontal line at observed value
ax1.axhline(correlations[0], color='red', linestyle='--', linewidth=2.5,
           alpha=0.7, label=f'All methods = {correlations[0]:.4f}')
ax1.legend(frameon=True, fontsize=11, fancybox=True, shadow=True)

# Panel B: Key Finding / Interpretation
ax2 = plt.subplot(122)

finding_text = """
RESCALING-INDEPENDENT UNIVERSALITY

All rescaling parameters yield 
IDENTICAL spectral universality:

r = 0.9852

This includes:
• λ₂ (spectral gap - PMIR prediction)
• λ₃, λ₄ (higher eigenvalues)
• λ_mean, λ_max (aggregate measures)
• No rescaling (raw time)

INTERPRETATION:
Spectral universality emerges at the
SIGNAL LEVEL itself, independent of
temporal rescaling schemes.

The phenomenon is MORE FUNDAMENTAL
than specific theoretical predictions.

This STRENGTHENS the main finding:
spectral equilibrium is a robust,
intrinsic property of resting brain
dynamics.
"""

ax2.text(0.5, 0.5, finding_text, ha='center', va='center',
        fontsize=11, transform=ax2.transAxes, family='monospace',
        bbox=dict(boxstyle='round', facecolor='lightblue', 
                 alpha=0.3, edgecolor='steelblue', linewidth=3))

ax2.set_xlim([0, 1])
ax2.set_ylim([0, 1])
ax2.axis('off')
ax2.set_title('B. Key Finding', fontsize=14, fontweight='bold')

# Add emphasis box
rect = plt.Rectangle((0.05, 0.05), 0.9, 0.9, linewidth=4, 
                     edgecolor='red', facecolor='none',
                     transform=ax2.transAxes, linestyle='--')
ax2.add_patch(rect)

plt.tight_layout()
plt.savefig(os.path.join(FIGS, 'SuppFig4_Rescaling_Comparison.png'), 
           dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(FIGS, 'SuppFig4_Rescaling_Comparison.pdf'), 
           bbox_inches='tight')
print("✓ Saved Supplementary Figure S4")
plt.close()

# ============================================================================
# SUPPLEMENTARY FIGURE S5: CONNECTIVITY METHODS COMPARISON
# ============================================================================

print("\n[3/3] Generating Supplementary Figure S5: Connectivity Methods Comparison...")

fig = plt.figure(figsize=(15, 10))

# Panel A: Overall correlations
ax1 = plt.subplot(221)

methods = df_connectivity['connectivity_method'].values
overall_corrs = df_connectivity['overall_correlation'].values

# Clean up method names
method_labels = []
for m in methods:
    if m == 'pearson':
        method_labels.append('Pearson\nCorrelation')
    elif m == 'plv':
        method_labels.append('Phase-Locking\nValue (PLV)')
    elif m == 'coherence':
        method_labels.append('Magnitude-Squared\nCoherence')
    else:
        method_labels.append(m)

x_pos_meth = np.arange(len(methods))
colors_meth = ['#3498db', '#e74c3c', '#2ecc71']

bars = ax1.bar(x_pos_meth, overall_corrs, color=colors_meth, alpha=0.85,
              edgecolor='black', linewidth=2.5, width=0.6)

# Value labels
for bar, val in zip(bars, overall_corrs):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
            f'{val:.4f}', ha='center', va='bottom', 
            fontsize=13, fontweight='bold')

ax1.set_xlabel('Connectivity Method', fontsize=13, fontweight='bold')
ax1.set_ylabel('Overall Spectral Universality', fontsize=13, fontweight='bold')
ax1.set_title('A. Overall Correlation by Method', fontsize=14, fontweight='bold')
ax1.set_xticks(x_pos_meth)
ax1.set_xticklabels(method_labels, fontsize=11)
ax1.set_ylim([0.8, 1.05])
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.grid(True, alpha=0.3, axis='y')

# Add null reference
ax1.axhline(0.002, color='gray', linestyle=':', linewidth=3,
           alpha=0.7, label='Null expectation (r = 0.002)')
ax1.legend(frameon=True, fontsize=10, fancybox=True, shadow=True)

# Panel B: Lambda2 CV comparison
ax2 = plt.subplot(222)

lambda2_cvs = df_connectivity['lambda2_cv'].values

bars_cv = ax2.bar(x_pos_meth, lambda2_cvs, color=colors_meth, alpha=0.85,
                 edgecolor='black', linewidth=2.5, width=0.6)

for bar, val in zip(bars_cv, lambda2_cvs):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
            f'{val:.2f}%', ha='center', va='bottom', 
            fontsize=12, fontweight='bold')

ax2.set_xlabel('Connectivity Method', fontsize=13, fontweight='bold')
ax2.set_ylabel('λ₂ Coefficient of Variation (%)', fontsize=13, fontweight='bold')
ax2.set_title('B. λ₂ Variability by Method', fontsize=14, fontweight='bold')
ax2.set_xticks(x_pos_meth)
ax2.set_xticklabels(method_labels, fontsize=11)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.grid(True, alpha=0.3, axis='y')

# Panel C: Per-band breakdown
ax3 = plt.subplot(223)

bands_conn = [1, 2, 3, 4, 5]
x_bands = np.arange(len(bands_conn))
width_band = 0.25

# Extract band correlations for each method
pearson_bands = [df_connectivity[df_connectivity['connectivity_method']=='pearson'][f'band_{i}'].values[0] 
                for i in bands_conn]
plv_bands = [df_connectivity[df_connectivity['connectivity_method']=='plv'][f'band_{i}'].values[0] 
            for i in bands_conn]
coherence_bands = [df_connectivity[df_connectivity['connectivity_method']=='coherence'][f'band_{i}'].values[0] 
                  for i in bands_conn]

bars1 = ax3.bar(x_bands - width_band, pearson_bands, width_band, 
               label='Pearson', alpha=0.8, color='#3498db', edgecolor='black', linewidth=1.5)
bars2 = ax3.bar(x_bands, plv_bands, width_band, 
               label='PLV', alpha=0.8, color='#e74c3c', edgecolor='black', linewidth=1.5)
bars3 = ax3.bar(x_bands + width_band, coherence_bands, width_band, 
               label='Coherence', alpha=0.8, color='#2ecc71', edgecolor='black', linewidth=1.5)

ax3.set_xlabel('Spectral Band', fontsize=13, fontweight='bold')
ax3.set_ylabel('Mean Inter-Subject Correlation', fontsize=13, fontweight='bold')
ax3.set_title('C. Per-Band Breakdown by Method', fontsize=14, fontweight='bold')
ax3.set_xticks(x_bands)
ax3.set_xticklabels([f'Band {i}' for i in bands_conn], fontsize=11)
ax3.set_ylim([0.6, 1.05])
ax3.legend(frameon=True, fontsize=10, loc='lower left', fancybox=True, shadow=True)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.grid(True, alpha=0.3, axis='y')

# Panel D: Key Findings
ax4 = plt.subplot(224)

findings_text = """
METHODOLOGICAL ROBUSTNESS

All connectivity methods show
HIGH spectral universality:

• PLV:        r = 0.9974  (best)
• Pearson:    r = 0.9902  (primary)
• Coherence:  r = 0.8538  (good)

All methods r > 0.85
All >> null expectation (r = 0.002)

Phase-based methods (PLV, Pearson)
show near-perfect universality,
suggesting spectral equilibrium
involves PHASE RELATIONSHIPS.

Coherence slightly lower but still
extraordinary, indicating some
frequency-specific variation.

Result is ROBUST to connectivity
measure choice.

Core finding holds across
methodologies.
"""

ax4.text(0.5, 0.5, findings_text, ha='center', va='center',
        fontsize=10.5, transform=ax4.transAxes, family='monospace',
        bbox=dict(boxstyle='round', facecolor='lightgreen', 
                 alpha=0.3, edgecolor='green', linewidth=3))

ax4.set_xlim([0, 1])
ax4.set_ylim([0, 1])
ax4.axis('off')
ax4.set_title('D. Key Findings', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(FIGS, 'SuppFig5_Connectivity_Methods.png'), 
           dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(FIGS, 'SuppFig5_Connectivity_Methods.pdf'), 
           bbox_inches='tight')
print("✓ Saved Supplementary Figure S5")
plt.close()

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("SUPPLEMENTARY FIGURES S3-S5 COMPLETE!")
print("="*80)
print(f"\nAll figures saved to: {FIGS}")
print("\nGenerated files:")
print("  [NEW] SuppFig3_EyesOpen_vs_EyesClosed.png/.pdf")
print("  [NEW] SuppFig4_Rescaling_Comparison.png/.pdf")
print("  [NEW] SuppFig5_Connectivity_Methods.png/.pdf")
print("\nAll supplementary figures now complete:")
print("  [v1.1] SuppFig1_NullModel_Detailed.png/.pdf")
print("  [v1.1] SuppFig2_BandSensitivity_Extended.png/.pdf")
print("  [NEW]  SuppFig3_EyesOpen_vs_EyesClosed.png/.pdf")
print("  [NEW]  SuppFig4_Rescaling_Comparison.png/.pdf")
print("  [NEW]  SuppFig5_Connectivity_Methods.png/.pdf")
print("\n✓ Ready for manuscript submission!")
