"""
Download ABIDE data via nilearn.
Run from anywhere with: python download_abide.py
"""
from nilearn import datasets

print("Downloading ABIDE (100 subjects, ~1.5 GB, ~15-20 min)...")

data = datasets.fetch_abide_pcp(
    data_dir=r"C:\Users\veilbreaker\PMIR_Research\paper1_brain_universality\data\abide",
    pipeline="cpac",
    band_pass_filtering=True,
    global_signal_regression=False,
    derivatives=["rois_cc200"],
    n_subjects=100,
    verbose=1
)

print(f"\nDone. Downloaded {len(data.rois_cc200)} subjects.")
print(f"First file: {data.rois_cc200[0]}")
