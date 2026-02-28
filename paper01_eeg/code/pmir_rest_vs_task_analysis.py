#!/usr/bin/env python3
"""
PMIR CRITICAL TEST: REST vs TASK ANALYSIS
Tests whether externally-driven systems show spectral band collapse

Author: Richard L Schorr III
Date: February 2026

SETUP:
1. Install required packages:
   pip install numpy scipy matplotlib pandas

2. Update the DATA_PATH below to point to your EDF files

3. Run:
   python pmir_rest_vs_task_analysis.py
"""

import numpy as np
import struct
import matplotlib.pyplot as plt
from scipy import stats
import pandas as pd
import os
from pathlib import Path

# ============================================================================
# CONFIGURATION - UPDATE THIS PATH!
# ============================================================================

# Point this to the folder containing your EDF files
DATA_PATH = r'C:\Users\veilbreaker\Downloads\PMIR_neurology\DataPulls'

# Output directory (will be created if it doesn't exist)
OUTPUT_PATH = r'C:\Users\veilbreaker\Downloads\PMIR_neurology\RestVsTask_Results'

# ============================================================================
# EDF FILE READER
# ============================================================================

def safe_float(s):
    """Safely convert string to float."""
    s = s.strip()
    return float(s) if s else 0.0

def safe_int(s):
    """Safely convert string to int."""
    s = s.strip()
    return int(s) if s else 0

def read_edf_file(filepath):
    """
    Read European Data Format (EDF) file.
    
    Returns:
        data: (n_channels, n_samples) array
        labels: list of channel names
        fs: sampling frequency
    """
    with open(filepath, 'rb') as f:
        # Read header (256 bytes)
        header = f.read(256)
        
        n_signals = int(header[252:256].decode('ascii', errors='ignore').strip())
        n_records = int(header[236:244].decode('ascii', errors='ignore').strip())
        record_duration = safe_float(header[244:252].decode('ascii', errors='ignore'))
        
        # Read signal headers
        labels = [f.read(16).decode('ascii', errors='ignore').strip() for _ in range(n_signals)]
        f.read(80 * n_signals)  # transducer
        f.read(8 * n_signals)   # physical_dim
        
        physical_mins = [safe_float(f.read(8).decode('ascii', errors='ignore')) for _ in range(n_signals)]
        physical_maxs = [safe_float(f.read(8).decode('ascii', errors='ignore')) for _ in range(n_signals)]
        digital_mins = [safe_int(f.read(8).decode('ascii', errors='ignore')) for _ in range(n_signals)]
        digital_maxs = [safe_int(f.read(8).decode('ascii', errors='ignore')) for _ in range(n_signals)]
        
        f.read(80 * n_signals)  # prefilter
        n_samples_list = [safe_int(f.read(8).decode('ascii', errors='ignore')) for _ in range(n_signals)]
        f.read(32 * n_signals)  # reserved
        
        # Calculate sampling frequency
        fs = n_samples_list[0] / record_duration if record_duration > 0 else 160
        
        # Read data records
        all_data = [[] for _ in range(n_signals)]
        
        for rec in range(n_records):
            for sig_idx in range(n_signals):
                n_samp = n_samples_list[sig_idx]
                for _ in range(n_samp):
                    try:
                        val = struct.unpack('<h', f.read(2))[0]
                        all_data[sig_idx].append(val)
                    except:
                        pass
        
        # Truncate to minimum length across channels
        min_len = min(len(x) for x in all_data)
        data_array = np.zeros((n_signals, min_len))
        
        # Scale to physical values
        for sig_idx in range(n_signals):
            if digital_maxs[sig_idx] != digital_mins[sig_idx]:
                scale = (physical_maxs[sig_idx] - physical_mins[sig_idx]) / \
                        (digital_maxs[sig_idx] - digital_mins[sig_idx])
            else:
                scale = 1.0
            
            offset = physical_mins[sig_idx] - scale * digital_mins[sig_idx]
            physical = [x * scale + offset for x in all_data[sig_idx][:min_len]]
            data_array[sig_idx, :] = physical
        
        return data_array, labels, fs

# ============================================================================
# SPECTRAL ANALYSIS FUNCTIONS
# ============================================================================

def compute_functional_connectivity(data):
    """Compute correlation-based functional connectivity matrix."""
    conn = np.corrcoef(data)
    np.fill_diagonal(conn, 0)
    conn = np.abs(conn)
    return conn

def compute_graph_laplacian(connectivity_matrix):
    """Compute normalized graph Laplacian."""
    # Degree matrix
    D = np.diag(connectivity_matrix.sum(axis=1))
    
    # Normalized Laplacian: L = I - D^(-1/2) A D^(-1/2)
    D_inv_sqrt = np.diag(1.0 / np.sqrt(np.diag(D) + 1e-10))
    L = np.eye(len(D)) - D_inv_sqrt @ connectivity_matrix @ D_inv_sqrt
    
    return L

def compute_spectral_properties(data):
    """
    Compute spectral properties of EEG data.
    
    Returns:
        eigenvalues: sorted eigenvalues
        eigenvectors: corresponding eigenvectors
        lambda_2: spectral gap (2nd smallest eigenvalue)
    """
    # Functional connectivity
    conn = compute_functional_connectivity(data)
    
    # Laplacian
    L = compute_graph_laplacian(conn)
    
    # Eigendecomposition
    eigenvals, eigenvecs = np.linalg.eigh(L)
    
    # Sort
    idx = eigenvals.argsort()
    eigenvals = eigenvals[idx]
    eigenvecs = eigenvecs[:, idx]
    
    lambda_2 = eigenvals[1]
    
    return eigenvals, eigenvecs, lambda_2

def project_onto_spectral_band(data, eigenvectors, band_start, band_end):
    """
    Project time series data onto a spectral band.
    
    Returns:
        band_power: (n_timepoints,) power in this spectral band
    """
    # Get eigenvectors for this band
    band_vecs = eigenvectors[:, band_start:band_end]
    
    # Project data onto band eigenvectors
    # data: (n_channels, n_time)
    # eigenvectors: (n_channels, n_band_modes)
    # result: (n_time, n_band_modes)
    projections = data.T @ band_vecs
    
    # Band power: sum of squared projections
    band_power = np.sum(projections**2, axis=1)
    
    return band_power

def compute_band_correlations(data_dict, spectral_dict, n_bands=5):
    """
    Compute inter-subject correlations for each spectral band.
    
    Returns:
        band_correlations: list of dicts with correlation statistics
        overall_correlation: mean across all bands
    """
    n_channels = list(data_dict.values())[0]['data'].shape[0]
    band_size = n_channels // n_bands
    
    # Project each subject's data onto spectral bands
    band_dynamics = {}
    
    for subj in sorted(data_dict.keys()):
        data = data_dict[subj]['data']
        eigenvecs = spectral_dict[subj]['eigenvectors']
        lambda_2 = spectral_dict[subj]['lambda_2']
        fs = data_dict[subj]['fs']
        
        # Rescaled time
        n_samples = data.shape[1]
        t_rescaled = lambda_2 * np.arange(n_samples) / fs
        
        subj_bands = {}
        
        for band_idx in range(n_bands):
            # Band boundaries
            start = band_idx * band_size
            end = (band_idx + 1) * band_size if band_idx < n_bands - 1 else n_channels
            
            # Project onto band
            band_power = project_onto_spectral_band(data, eigenvecs, start, end)
            
            # Smooth
            window = 50
            band_power_smooth = np.convolve(band_power, np.ones(window)/window, mode='same')
            
            subj_bands[f'band_{band_idx+1}'] = band_power_smooth
        
        band_dynamics[subj] = subj_bands
    
    # Compute pairwise correlations for each band
    correlations = []
    
    for band_idx in range(n_bands):
        band_name = f'band_{band_idx+1}'
        
        # Get all subjects' data for this band (truncate to same length)
        min_len = min(len(band_dynamics[subj][band_name]) for subj in data_dict.keys())
        
        band_powers = []
        for subj in sorted(data_dict.keys()):
            power = band_dynamics[subj][band_name][:min_len]
            # Normalize
            power_norm = (power - power.mean()) / (power.std() + 1e-10)
            band_powers.append(power_norm)
        
        band_powers = np.array(band_powers)
        
        # Compute all pairwise correlations
        n_subjects = len(data_dict)
        band_corrs = []
        
        for i in range(n_subjects):
            for j in range(i+1, n_subjects):
                corr, _ = stats.pearsonr(band_powers[i], band_powers[j])
                band_corrs.append(corr)
        
        correlations.append({
            'band': band_idx + 1,
            'mean_corr': np.mean(band_corrs),
            'std_corr': np.std(band_corrs),
            'n_pairs': len(band_corrs)
        })
    
    # Overall correlation
    overall = np.mean([c['mean_corr'] for c in correlations])
    
    return correlations, overall

# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def main():
    print("="*80)
    print("PMIR CRITICAL TEST: REST vs TASK ANALYSIS")
    print("Testing: Do externally-driven systems show spectral band collapse?")
    print("="*80)
    
    # Create output directory
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    
    # Subject IDs
    subjects = [f'S{i:03d}' for i in range(1, 11)]
    
    # ========================================================================
    # STEP 1: Load Data
    # ========================================================================
    
    print("\n" + "="*80)
    print("STEP 1: LOADING DATA")
    print("="*80)
    
    rest_data = {}
    task_data = {}
    
    print("\nLOADING REST (R02) DATA...")
    for subj in subjects:
        filepath = os.path.join(DATA_PATH, f'{subj}R02.edf')
        try:
            data, channels, fs = read_edf_file(filepath)
            rest_data[subj] = {'data': data, 'fs': fs, 'channels': channels}
            print(f"✓ {subj}: {data.shape[0]} channels, {data.shape[1]} samples")
        except Exception as e:
            print(f"✗ {subj}: {e}")
    
    print(f"\n✓ Loaded {len(rest_data)} rest recordings")
    
    print("\nLOADING TASK (R04) DATA...")
    for subj in subjects:
        filepath = os.path.join(DATA_PATH, f'{subj}R04.edf')
        try:
            data, channels, fs = read_edf_file(filepath)
            task_data[subj] = {'data': data, 'fs': fs, 'channels': channels}
            print(f"✓ {subj}: {data.shape[0]} channels, {data.shape[1]} samples")
        except Exception as e:
            print(f"✗ {subj}: {e}")
    
    print(f"\n✓ Loaded {len(task_data)} task recordings")
    
    if len(rest_data) < 5 or len(task_data) < 5:
        print(f"\nERROR: Need at least 5 subjects for both conditions")
        print(f"Have: {len(rest_data)} rest, {len(task_data)} task")
        return
    
    # ========================================================================
    # STEP 2: Compute Spectral Properties
    # ========================================================================
    
    print("\n" + "="*80)
    print("STEP 2: COMPUTING SPECTRAL PROPERTIES")
    print("="*80)
    
    rest_spectral = {}
    task_spectral = {}
    
    print("\nREST (R02):")
    for subj in sorted(rest_data.keys()):
        eigenvals, eigenvecs, lambda_2 = compute_spectral_properties(rest_data[subj]['data'])
        rest_spectral[subj] = {
            'eigenvalues': eigenvals,
            'eigenvectors': eigenvecs,
            'lambda_2': lambda_2
        }
        print(f"{subj}: λ₂={lambda_2:.6f}")
    
    print("\nTASK (R04):")
    for subj in sorted(task_data.keys()):
        eigenvals, eigenvecs, lambda_2 = compute_spectral_properties(task_data[subj]['data'])
        task_spectral[subj] = {
            'eigenvalues': eigenvals,
            'eigenvectors': eigenvecs,
            'lambda_2': lambda_2
        }
        print(f"{subj}: λ₂={lambda_2:.6f}")
    
    # ========================================================================
    # STEP 3: Band Collapse Analysis
    # ========================================================================
    
    print("\n" + "="*80)
    print("STEP 3: SPECTRAL BAND COLLAPSE ANALYSIS")
    print("="*80)
    
    n_bands = 5
    
    print("\nComputing REST band correlations...")
    rest_corrs, rest_overall = compute_band_correlations(rest_data, rest_spectral, n_bands)
    
    print("\nREST (R02):")
    for c in rest_corrs:
        print(f"  Band {c['band']}: r={c['mean_corr']:.4f} ± {c['std_corr']:.4f}")
    print(f"  OVERALL: r={rest_overall:.4f}")
    
    print("\nComputing TASK band correlations...")
    task_corrs, task_overall = compute_band_correlations(task_data, task_spectral, n_bands)
    
    print("\nTASK (R04):")
    for c in task_corrs:
        print(f"  Band {c['band']}: r={c['mean_corr']:.4f} ± {c['std_corr']:.4f}")
    print(f"  OVERALL: r={task_overall:.4f}")
    
    # ========================================================================
    # STEP 4: Statistical Comparison
    # ========================================================================
    
    print("\n" + "="*80)
    print("STEP 4: PMIR PREDICTION TEST")
    print("="*80)
    
    difference = task_overall - rest_overall
    improvement = (difference / abs(rest_overall) * 100) if rest_overall != 0 else 0
    
    print(f"\nOverall inter-subject correlations:")
    print(f"  REST (no driving):   r = {rest_overall:.4f}")
    print(f"  TASK (with driving): r = {task_overall:.4f}")
    print(f"  DIFFERENCE:          Δr = {difference:.4f}")
    print(f"  IMPROVEMENT:         {improvement:.1f}%")
    
    print("\nPMIR Prediction:")
    print("  Externally-driven systems should show HIGHER band collapse")
    
    # Determine verdict
    if task_overall > rest_overall + 0.1:
        verdict = "✓✓ STRONG SUPPORT"
        interpretation = "Task-based shows significantly better collapse!"
    elif task_overall > rest_overall:
        verdict = "✓ MODERATE SUPPORT"
        interpretation = "Task-based shows improved collapse"
    elif task_overall > rest_overall - 0.05:
        verdict = "⚠ WEAK SUPPORT"
        interpretation = "Task and rest similar"
    else:
        verdict = "✗ NO SUPPORT"
        interpretation = "Task worse than rest (unexpected)"
    
    print(f"\n{verdict}")
    print(f"{interpretation}")
    
    # ========================================================================
    # STEP 5: Generate Figures
    # ========================================================================
    
    print("\n" + "="*80)
    print("STEP 5: GENERATING FIGURES")
    print("="*80)
    
    # Figure: Comparison
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))
    
    # Panel 1: Band correlations
    bands = np.arange(1, n_bands+1)
    rest_means = [c['mean_corr'] for c in rest_corrs]
    task_means = [c['mean_corr'] for c in task_corrs]
    
    x = np.arange(len(bands))
    width = 0.35
    
    ax1.bar(x - width/2, rest_means, width, label='Rest (R02)', alpha=0.7, color='blue')
    ax1.bar(x + width/2, task_means, width, label='Task (R04)', alpha=0.7, color='red')
    ax1.set_xlabel('Spectral Band', fontsize=12)
    ax1.set_ylabel('Mean Inter-Subject Correlation', fontsize=12)
    ax1.set_title('Band Collapse: Rest vs Task', fontsize=14)
    ax1.set_xticks(x)
    ax1.set_xticklabels([f'Band {i}' for i in bands])
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    
    # Panel 2: Overall comparison
    conditions = ['Rest\n(No Driving)', 'Task\n(With Driving)']
    overalls = [rest_overall, task_overall]
    colors_bar = ['blue', 'red']
    
    ax2.bar(conditions, overalls, color=colors_bar, alpha=0.7, edgecolor='black')
    ax2.set_ylabel('Overall Mean Correlation', fontsize=12)
    ax2.set_title('PMIR Test: External Driving Effect', fontsize=14)
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for i, v in enumerate(overalls):
        ax2.text(i, v + 0.01, f'{v:.4f}', ha='center', va='bottom', 
                fontsize=12, fontweight='bold')
    
    # Panel 3: Improvement
    ax3.bar(['Collapse\nImprovement'], [difference], 
            color='green' if difference > 0 else 'orange', 
            alpha=0.7, edgecolor='black')
    ax3.set_ylabel('Δ Correlation (Task - Rest)', fontsize=12)
    ax3.set_title('Effect of External Driving', fontsize=14)
    ax3.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.text(0, difference + 0.005, f'{difference:.4f}', 
            ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    plt.suptitle(f'PMIR Validation: {verdict}', fontsize=16, y=1.02)
    plt.tight_layout()
    
    fig_path = os.path.join(OUTPUT_PATH, 'rest_vs_task_comparison.png')
    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {fig_path}")
    plt.close()
    
    # ========================================================================
    # STEP 6: Save Results
    # ========================================================================
    
    print("\n" + "="*80)
    print("STEP 6: SAVING RESULTS")
    print("="*80)
    
    # Summary results
    results = {
        'rest_overall_correlation': rest_overall,
        'task_overall_correlation': task_overall,
        'difference': difference,
        'improvement_percent': improvement,
        'verdict': verdict,
        'interpretation': interpretation,
        'n_subjects': len(task_data)
    }
    
    df_results = pd.DataFrame([results])
    results_path = os.path.join(OUTPUT_PATH, 'summary_results.csv')
    df_results.to_csv(results_path, index=False)
    print(f"✓ Saved: {results_path}")
    
    # Band correlations
    df_rest = pd.DataFrame(rest_corrs)
    df_rest['condition'] = 'rest'
    df_task = pd.DataFrame(task_corrs)
    df_task['condition'] = 'task'
    
    df_bands = pd.concat([df_rest, df_task])
    bands_path = os.path.join(OUTPUT_PATH, 'band_correlations.csv')
    df_bands.to_csv(bands_path, index=False)
    print(f"✓ Saved: {bands_path}")
    
    # Spectral properties
    spectral_data = []
    for subj in sorted(rest_spectral.keys()):
        spectral_data.append({
            'subject': subj,
            'condition': 'rest',
            'lambda_2': rest_spectral[subj]['lambda_2']
        })
    for subj in sorted(task_spectral.keys()):
        spectral_data.append({
            'subject': subj,
            'condition': 'task',
            'lambda_2': task_spectral[subj]['lambda_2']
        })
    
    df_spectral = pd.DataFrame(spectral_data)
    spectral_path = os.path.join(OUTPUT_PATH, 'spectral_properties.csv')
    df_spectral.to_csv(spectral_path, index=False)
    print(f"✓ Saved: {spectral_path}")
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print(f"\n{verdict}")
    print(f"Task correlation: r={task_overall:.4f}")
    print(f"Rest correlation: r={rest_overall:.4f}")
    print(f"Improvement: {improvement:.1f}%")
    print(f"\nAll results saved to: {OUTPUT_PATH}")

if __name__ == '__main__':
    main()
