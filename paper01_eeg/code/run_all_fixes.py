#!/usr/bin/env python3
"""
MASTER SCRIPT - RUN ALL 4 MAJOR FIXES
Executes all validation analyses in correct order

Author: Richard L Schorr III
Date: February 2026
"""

import subprocess
import sys
import os
from datetime import datetime

BASE = r'C:\Users\veilbreaker\Downloads\PMIR_neurology\PMIR_EEG_Paper\02_Analysis_Scripts'

print("="*80)
print("RUNNING ALL 4 MAJOR FIXES FOR MANUSCRIPT v1.1")
print("="*80)
print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# List of scripts to run
scripts = [
    ('fix1_multiple_comparisons.py', 'Multiple Comparisons Correction', '30 min'),
    ('fix2_eyes_open_control.py', 'Eyes-Open Control Analysis', '2-3 hours'),
    ('fix3_lambda2_validation.py', 'Lambda2 Rescaling Validation', '2 hours'),
    ('fix4_alternative_connectivity.py', 'Alternative Connectivity Methods', '4 hours')
]

results = []

for i, (script, name, est_time) in enumerate(scripts, 1):
    print(f"\n{'='*80}")
    print(f"FIX {i}/4: {name}")
    print(f"Estimated time: {est_time}")
    print(f"{'='*80}\n")
    
    script_path = os.path.join(BASE, script)
    
    if not os.path.exists(script_path):
        print(f"⚠ WARNING: Script not found: {script_path}")
        print(f"Skipping...")
        results.append((name, 'SKIPPED', 'File not found'))
        continue
    
    start_time = datetime.now()
    
    try:
        # Run script
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=3600*5  # 5 hour timeout
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60  # minutes
        
        if result.returncode == 0:
            print(f"\n✓ SUCCESS - Completed in {duration:.1f} minutes")
            results.append((name, 'SUCCESS', f'{duration:.1f} min'))
        else:
            print(f"\n✗ FAILED - Return code: {result.returncode}")
            print(f"Error output:")
            print(result.stderr)
            results.append((name, 'FAILED', f'Error code {result.returncode}'))
    
    except subprocess.TimeoutExpired:
        print(f"\n✗ TIMEOUT - Exceeded 5 hours")
        results.append((name, 'TIMEOUT', '>5 hours'))
    
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        results.append((name, 'ERROR', str(e)))

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("ALL FIXES COMPLETE - SUMMARY")
print("="*80)
print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

print(f"{'Fix':<50} {'Status':<15} {'Time':<15}")
print("-" * 80)
for name, status, time in results:
    status_symbol = "✓" if status == "SUCCESS" else "✗"
    print(f"{status_symbol} {name:<48} {status:<15} {time:<15}")

print("\n" + "="*80)

# Check if all succeeded
all_success = all(status == 'SUCCESS' for _, status, _ in results)

if all_success:
    print("✓✓✓ ALL FIXES COMPLETED SUCCESSFULLY!")
    print("\nNext steps:")
    print("1. Review new results in 03_Results/ and 06_Supplementary/")
    print("2. Update manuscript with new sections")
    print("3. Regenerate figures if needed")
    print("4. Final manuscript review")
    print("5. Submit to bioRxiv + eLife")
else:
    print("⚠ SOME FIXES FAILED - Review errors above")
    print("\nSuccessful fixes can still be used.")
    print("Failed fixes can be run individually for debugging.")

print("\n" + "="*80)
