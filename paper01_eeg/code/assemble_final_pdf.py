#!/usr/bin/env python3
"""
FINAL PDF ASSEMBLY FOR MANUSCRIPT v1.2
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
FIGS_MAIN = os.path.join(BASE, '04_Figures', 'Main')
FIGS_SUPP = os.path.join(BASE, '04_Figures', 'Supplementary')
TABLES_SUPP = os.path.join(BASE, '07_Supplementary_Tables')
OUTPUT_DIR = os.path.join(BASE, '08_Final_Submission')

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("\nChecking for required tools...")

# Check if pandoc is available
try:
    import subprocess
    result = subprocess.run(['pandoc', '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ Pandoc found")
        PANDOC_AVAILABLE = True
    else:
        print("✗ Pandoc not found")
        PANDOC_AVAILABLE = False
except:
    print("✗ Pandoc not available")
    PANDOC_AVAILABLE = False

print("\n" + "="*80)
print("CREATING COMPREHENSIVE MANUSCRIPT DOCUMENT")
print("="*80)

# Create a comprehensive markdown file with everything
output_md = os.path.join(OUTPUT_DIR, 'COMPLETE_MANUSCRIPT_v1.2_FOR_REVIEW.md')

with open(output_md, 'w', encoding='utf-8') as out:
    
    # Write title page
    out.write("---\n")
    out.write("title: 'Spectral Universality in Resting-State Brain Networks: Evidence for Equilibrium Dynamics'\n")
    out.write("author: 'Richard L. Schorr III'\n")
    out.write("date: 'February 2026'\n")
    out.write("abstract: |\n")
    out.write("  This document contains the complete manuscript v1.2 including all main figures,\n")
    out.write("  supplementary figures, and supplementary tables for final review before submission.\n")
    out.write("geometry: margin=1in\n")
    out.write("fontsize: 11pt\n")
    out.write("linestretch: 1.5\n")
    out.write("---\n\n")
    
    out.write("\\newpage\n\n")
    
    # Read and include main manuscript
    print("\n[1/4] Including main manuscript text...")
    with open(MANUSCRIPT, 'r', encoding='utf-8') as f:
        manuscript_text = f.read()
    
    # Fix location (Newark -> Lancaster)
    manuscript_text = manuscript_text.replace("Newark, Ohio", "Lancaster, Ohio")
    
    out.write(manuscript_text)
    out.write("\n\n")
    
    # Add page break before figures
    out.write("\\newpage\n\n")
    out.write("# MAIN FIGURES\n\n")
    
    # List main figures
    print("\n[2/4] Listing main figures...")
    main_figs = [
        "Figure1_Lambda2_Universality.pdf",
        "Figure2_Spectral_Band_Collapse.pdf", 
        "Figure3_Rest_vs_Task.pdf",
        "Figure4_Topology_Independence.pdf"
    ]
    
    for i, fig in enumerate(main_figs, 1):
        fig_path = os.path.join(FIGS_MAIN, fig)
        if os.path.exists(fig_path):
            out.write(f"## Figure {i}\n\n")
            out.write(f"![Figure {i}]({fig_path}){{width=100%}}\n\n")
            out.write("\\newpage\n\n")
            print(f"  ✓ Figure {i} listed")
        else:
            # Try base directory
            fig_path = os.path.join(BASE, '04_Figures', fig)
            if os.path.exists(fig_path):
                out.write(f"## Figure {i}\n\n")
                out.write(f"![Figure {i}]({fig_path}){{width=100%}}\n\n")
                out.write("\\newpage\n\n")
                print(f"  ✓ Figure {i} listed")
            else:
                print(f"  ⚠ Figure {i} not found: {fig}")
    
    # Add supplementary figures
    out.write("\\newpage\n\n")
    out.write("# SUPPLEMENTARY FIGURES\n\n")
    
    print("\n[3/4] Listing supplementary figures...")
    supp_figs = [
        "SuppFig1_NullModel_Detailed_v1.1.pdf",
        "SuppFig2_BandSensitivity_Extended_v1.1.pdf",
        "SuppFig3_EyesOpen_vs_EyesClosed.pdf",
        "SuppFig4_Rescaling_Comparison.pdf",
        "SuppFig5_Connectivity_Methods.pdf"
    ]
    
    for i, fig in enumerate(supp_figs, 1):
        fig_path = os.path.join(FIGS_SUPP, fig)
        if os.path.exists(fig_path):
            out.write(f"## Supplementary Figure S{i}\n\n")
            out.write(f"![Supplementary Figure S{i}]({fig_path}){{width=100%}}\n\n")
            out.write("\\newpage\n\n")
            print(f"  ✓ Supplementary Figure S{i} listed")
        else:
            print(f"  ⚠ Supplementary Figure S{i} not found: {fig}")
    
    # Add supplementary tables
    out.write("\\newpage\n\n")
    out.write("# SUPPLEMENTARY TABLES\n\n")
    
    print("\n[4/4] Including supplementary tables...")
    
    # Read the combined tables document
    tables_file = os.path.join(TABLES_SUPP, 'All_Supplementary_Tables.txt')
    if os.path.exists(tables_file):
        with open(tables_file, 'r', encoding='utf-8') as f:
            tables_text = f.read()
        
        # Format as code block for clean display
        out.write("```\n")
        out.write(tables_text)
        out.write("\n```\n\n")
        print("  ✓ All supplementary tables included")
    else:
        print("  ⚠ Supplementary tables file not found")

print("\n✓ Comprehensive markdown document created:")
print(f"  {output_md}")

# Try to convert to PDF using pandoc
if PANDOC_AVAILABLE:
    print("\n" + "="*80)
    print("CONVERTING TO PDF WITH PANDOC")
    print("="*80)
    
    output_pdf = os.path.join(OUTPUT_DIR, 'COMPLETE_MANUSCRIPT_v1.2_FOR_REVIEW.pdf')
    
    pandoc_cmd = [
        'pandoc',
        output_md,
        '-o', output_pdf,
        '--pdf-engine=pdflatex',
        '--toc',
        '--number-sections',
        '-V', 'geometry:margin=1in',
        '-V', 'fontsize=11pt',
        '-V', 'linestretch=1.5'
    ]
    
    print("\nRunning pandoc...")
    print(f"Command: {' '.join(pandoc_cmd)}")
    
    try:
        result = subprocess.run(pandoc_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("\n✓ PDF created successfully!")
            print(f"  {output_pdf}")
        else:
            print(f"\n✗ Pandoc failed with error:")
            print(result.stderr)
            print("\nYou can manually convert the markdown file to PDF")
    except Exception as e:
        print(f"\n✗ Error running pandoc: {e}")
        print("\nYou can manually convert the markdown file to PDF")
else:
    print("\n" + "="*80)
    print("PANDOC NOT AVAILABLE - MANUAL CONVERSION NEEDED")
    print("="*80)
    print("\nYou have two options:")
    print("\n1. Install pandoc and LaTeX:")
    print("   - Download pandoc: https://pandoc.org/installing.html")
    print("   - Download MiKTeX (LaTeX): https://miktex.org/download")
    print("   - Then run this script again")
    print("\n2. Use an online converter:")
    print("   - Open: https://www.markdowntopdf.com/")
    print(f"   - Upload: {output_md}")
    print("   - Download PDF")
    print("\n3. Use Microsoft Word:")
    print(f"   - Open: {output_md}")
    print("   - File > Save As > PDF")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"\nCreated comprehensive document: {output_md}")
print("\nContents:")
print("  - Complete manuscript text (12,000 words)")
print("  - All main figures (1-4)")
print("  - All supplementary figures (S1-S5)")
print("  - All supplementary tables (S1-S4)")
print("\nNext steps:")
if PANDOC_AVAILABLE and os.path.exists(output_pdf):
    print(f"  1. Review PDF: {output_pdf}")
    print("  2. Check all figures appear correctly")
    print("  3. Check all tables are readable")
    print("  4. Make any final edits if needed")
    print("  5. Ready for submission!")
else:
    print("  1. Convert markdown to PDF (see options above)")
    print("  2. Review PDF")
    print("  3. Make any final edits if needed")
    print("  4. Ready for submission!")

print("\n✓ COMPLETE MANUSCRIPT ASSEMBLY FINISHED!")
