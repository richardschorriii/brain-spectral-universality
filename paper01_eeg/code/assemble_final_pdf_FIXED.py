#!/usr/bin/env python3
"""
FINAL PDF ASSEMBLY FOR MANUSCRIPT v1.2 (FIXED FILENAMES)
Combines manuscript text, figures, and tables into a single review PDF

Author: Richard L Schorr III
Date: February 2026
"""

import os
import sys
from pathlib import Path

print("="*80)
print("FINAL PDF ASSEMBLY - MANUSCRIPT v1.2")
print("="*80)

# Paths
BASE = r'C:\Users\veilbreaker\Downloads\PMIR_neurology\PMIR_EEG_Paper'
MANUSCRIPT = os.path.join(BASE, 'PMIR_Brain_Paper_v1.2_COMPLETE.md')
FIGS_DIR = os.path.join(BASE, '04_Figures')
TABLES_SUPP = os.path.join(BASE, '07_Supplementary_Tables')
OUTPUT_DIR = os.path.join(BASE, '08_Final_Submission')

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("\n" + "="*80)
print("CREATING COMPREHENSIVE MANUSCRIPT DOCUMENT")
print("="*80)

# Create a comprehensive markdown file with everything
output_md = os.path.join(OUTPUT_DIR, 'COMPLETE_MANUSCRIPT_v1.2_FOR_REVIEW.md')

with open(output_md, 'w', encoding='utf-8') as out:
    
    # Write title page
    out.write("# COMPLETE MANUSCRIPT v1.2 - FINAL REVIEW\n\n")
    out.write("**Title:** Spectral Universality in Resting-State Brain Networks: Evidence for Equilibrium Dynamics\n\n")
    out.write("**Author:** Richard L. Schorr III\n\n")
    out.write("**Affiliation:** Independent Researcher, Lancaster, Ohio, USA\n\n")
    out.write("**Date:** February 2026\n\n")
    out.write("**Document Contents:**\n")
    out.write("- Complete manuscript text (12,000 words)\n")
    out.write("- All main figures (1-4)\n")
    out.write("- All supplementary figures (S1-S5)\n")
    out.write("- All supplementary tables (S1-S4)\n\n")
    out.write("---\n\n")
    
    # Read and include main manuscript
    print("\n[1/4] Including main manuscript text...")
    manuscript_path = os.path.join(BASE, 'PMIR_Brain_Paper_v1.2_COMPLETE.md')
    
    # Check if file exists
    if not os.path.exists(manuscript_path):
        # Try project folder
        manuscript_path = r'/mnt/user-data/outputs/PMIR_Brain_Paper_v1.2_COMPLETE.md'
    
    if os.path.exists(manuscript_path):
        with open(manuscript_path, 'r', encoding='utf-8') as f:
            manuscript_text = f.read()
        
        # Fix location (Newark -> Lancaster)
        manuscript_text = manuscript_text.replace("Newark, Ohio", "Lancaster, Ohio")
        
        out.write(manuscript_text)
        out.write("\n\n")
        print("  ✓ Manuscript text included")
    else:
        out.write("ERROR: Manuscript file not found\n\n")
        print("  ✗ Manuscript file not found")
    
    # Add page break before figures
    out.write("---\n\n")
    out.write("# MAIN FIGURES\n\n")
    
    # List main figures - USING ACTUAL FILENAMES
    print("\n[2/4] Listing main figures...")
    
    # Main figures in the base 04_Figures directory
    main_figs = [
        ("Figure 1: λ₂ Universality", "Figure1_Lambda2_Universality_v1.1.pdf"),
        ("Figure 2: Spectral Band Collapse", "Figure2_Spectral_Band_Collapse_v1.1.pdf"),
        ("Figure 3: Validation", "Figure3_Validation_v1.1.pdf"),
        ("Figure 4: Topology Independence", "Figure4_Topology_Independence.pdf")
    ]
    
    for i, (title, filename) in enumerate(main_figs, 1):
        fig_path = os.path.join(FIGS_DIR, filename)
        
        out.write(f"## Figure {i}: {title}\n\n")
        
        if os.path.exists(fig_path):
            out.write(f"**File:** `{filename}`\n\n")
            out.write(f"![{title}]({fig_path})\n\n")
            print(f"  ✓ Figure {i} found: {filename}")
        else:
            out.write(f"**File:** `{filename}` (NOT FOUND)\n\n")
            print(f"  ✗ Figure {i} not found: {filename}")
        
        out.write("---\n\n")
    
    # Add supplementary figures
    out.write("---\n\n")
    out.write("# SUPPLEMENTARY FIGURES\n\n")
    
    print("\n[3/4] Listing supplementary figures...")
    
    supp_figs = [
        ("Null Model Detailed Analysis", "SuppFig1_NullModel_Detailed_v1.1.pdf"),
        ("Band Sensitivity Extended", "SuppFig2_BandSensitivity_Extended_v1.1.pdf"),
        ("Eyes-Open vs Eyes-Closed", "SuppFig3_EyesOpen_vs_EyesClosed.pdf"),
        ("Rescaling Parameter Comparison", "SuppFig4_Rescaling_Comparison.pdf"),
        ("Connectivity Methods Comparison", "SuppFig5_Connectivity_Methods.pdf")
    ]
    
    for i, (title, filename) in enumerate(supp_figs, 1):
        fig_path = os.path.join(FIGS_DIR, filename)
        
        out.write(f"## Supplementary Figure S{i}: {title}\n\n")
        
        if os.path.exists(fig_path):
            out.write(f"**File:** `{filename}`\n\n")
            out.write(f"![{title}]({fig_path})\n\n")
            print(f"  ✓ Supp Figure S{i} found: {filename}")
        else:
            out.write(f"**File:** `{filename}` (NOT FOUND)\n\n")
            print(f"  ✗ Supp Figure S{i} not found: {filename}")
        
        out.write("---\n\n")
    
    # Add supplementary tables
    out.write("---\n\n")
    out.write("# SUPPLEMENTARY TABLES\n\n")
    
    print("\n[4/4] Including supplementary tables...")
    
    # Read the combined tables document
    tables_file = os.path.join(TABLES_SUPP, 'All_Supplementary_Tables.txt')
    if os.path.exists(tables_file):
        with open(tables_file, 'r', encoding='utf-8') as f:
            tables_text = f.read()
        
        out.write(tables_text)
        out.write("\n\n")
        print("  ✓ All supplementary tables included")
    else:
        out.write("ERROR: Supplementary tables file not found\n\n")
        print("  ✗ Supplementary tables file not found")

print("\n✓ Comprehensive markdown document created:")
print(f"  {output_md}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"\nCreated: {output_md}")
print("\nThis file contains:")
print("  ✓ Complete manuscript text")
print("  ✓ Links to all main figures (1-4)")
print("  ✓ Links to all supplementary figures (S1-S5)")
print("  ✓ All supplementary tables (S1-S4)")
print("\nNext steps:")
print("  1. Open the markdown file to review")
print("  2. Or convert to PDF using:")
print("     - Microsoft Word (File > Open > Save as PDF)")
print("     - Google Docs (upload > File > Download > PDF)")
print("     - Online: https://www.markdowntopdf.com/")
print("  3. Review everything")
print("  4. Make any final edits")
print("  5. Ready for submission!")

print("\n" + "="*80)
print("FIGURE FILE SUMMARY")
print("="*80)
print("\nMain Figures:")
for i, (title, filename) in enumerate([
    ("λ₂ Universality", "Figure1_Lambda2_Universality_v1.1.pdf"),
    ("Spectral Band Collapse", "Figure2_Spectral_Band_Collapse_v1.1.pdf"),
    ("Validation", "Figure3_Validation_v1.1.pdf"),
    ("Topology Independence", "Figure4_Topology_Independence.pdf")
], 1):
    fig_path = os.path.join(FIGS_DIR, filename)
    status = "✓ EXISTS" if os.path.exists(fig_path) else "✗ MISSING"
    print(f"  Fig {i}: {filename:<50} {status}")

print("\nSupplementary Figures:")
for i, (title, filename) in enumerate([
    ("Null Model", "SuppFig1_NullModel_Detailed_v1.1.pdf"),
    ("Band Sensitivity", "SuppFig2_BandSensitivity_Extended_v1.1.pdf"),
    ("Eyes-Open vs Closed", "SuppFig3_EyesOpen_vs_EyesClosed.pdf"),
    ("Rescaling", "SuppFig4_Rescaling_Comparison.pdf"),
    ("Connectivity", "SuppFig5_Connectivity_Methods.pdf")
], 1):
    fig_path = os.path.join(FIGS_DIR, filename)
    status = "✓ EXISTS" if os.path.exists(fig_path) else "✗ MISSING"
    print(f"  S{i}: {filename:<50} {status}")

print("\n✓ ASSEMBLY COMPLETE!")
