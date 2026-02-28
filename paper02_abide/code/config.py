"""
PAPER 1: Consciousness-State Spectral Universality Across the Human Connectome
Configuration file — all parameters live here. Modify this file to change any
aspect of the pipeline without touching analysis code.

PMIR Prediction: After rescaling eigenspectrum {λ₁=0, λ₂, λ₃, ..., λ_N} by λ₂,
the normalized spectral density ρ(λ/λ₂) collapses onto a universal curve across
subjects and consciousness states.
"""

import os

# ─────────────────────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
NULL_MODELS_DIR = os.path.join(BASE_DIR, "null_models")

# ─────────────────────────────────────────────────────────────────────────────
# DATASETS — toggle active datasets here
# ─────────────────────────────────────────────────────────────────────────────
DATASETS = {
    # PRIMARY: Raj Lab pre-computed HCP structural connectomes
    # Source: github.com/Raj-Lab-UCSF/spectrome
    # N=1,071 HCP Young Adult subjects
    "raj_lab_hcp": {
        "enabled": True,
        "type": "structural",
        "source": "raj_lab",
        "n_subjects_expected": 1071,
        "data_path": os.path.join(DATA_DIR, "raj_lab_hcp"),
        "url": "https://github.com/Raj-Lab-UCSF/spectrome",
        "notes": "Pre-computed connectomes, fastest path to N=1071"
    },

    # OpenNeuro ds003768: EEG+fMRI, resting + sleep stages (NREM1/2/3)
    # CC0 license. N=33 subjects.
    "openneuro_sleep": {
        "enabled": True,
        "type": "functional",
        "source": "openneuro",
        "dataset_id": "ds003768",
        "n_subjects_expected": 33,
        "data_path": os.path.join(DATA_DIR, "openneuro_sleep"),
        "states": ["wake", "NREM1", "NREM2", "NREM3"],
        "notes": "Consciousness-state variation: wake → deep sleep"
    },

    # OpenNeuro propofol dataset: mental imagery under graded sedation
    # N=26 subjects
    "openneuro_propofol": {
        "enabled": True,
        "type": "functional",
        "source": "openneuro",
        "n_subjects_expected": 26,
        "data_path": os.path.join(DATA_DIR, "openneuro_propofol"),
        "states": ["awake", "light_sedation", "deep_sedation"],
        "notes": "Covert consciousness during behavioral unresponsiveness"
    },

    # ABIDE I+II: autism spectrum + controls, 32 sites
    # Downloaded via nilearn.datasets.fetch_abide_pcp
    # N=2156 total
    "abide": {
        "enabled": True,
        "type": "functional",
        "source": "nilearn",
        "n_subjects_expected": 2156,
        "data_path": os.path.join(DATA_DIR, "abide"),
        "notes": "Clinical network variation, multi-site robustness test"
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# PARCELLATION SCHEMES — test independence across 3+ atlases
# ─────────────────────────────────────────────────────────────────────────────
PARCELLATIONS = {
    "desikan": {
        "enabled": True,
        "n_regions": 68,
        "atlas": "Desikan-Killiany",
        "notes": "Primary parcellation"
    },
    "glasser": {
        "enabled": True,
        "n_regions": 360,
        "atlas": "HCP MMP 1.0",
        "notes": "High-resolution multimodal parcellation"
    },
    "schaefer100": {
        "enabled": True,
        "n_regions": 100,
        "atlas": "Schaefer 2018",
        "resolution": 100,
    },
    "schaefer200": {
        "enabled": True,
        "n_regions": 200,
        "atlas": "Schaefer 2018",
        "resolution": 200,
    },
    "schaefer400": {
        "enabled": True,
        "n_regions": 400,
        "atlas": "Schaefer 2018",
        "resolution": 400,
    },
}
PRIMARY_PARCELLATION = "desikan"

# ─────────────────────────────────────────────────────────────────────────────
# CONNECTIVITY METHODS — test robustness across construction approaches
# ─────────────────────────────────────────────────────────────────────────────
CONNECTIVITY_METHODS = {
    "pearson": {
        "enabled": True,
        "type": "functional",
        "description": "Pearson correlation of BOLD time series",
        "threshold": 0.0,       # set >0 to threshold weak connections
        "absolute_value": True, # take |r| to ensure non-negative adjacency
    },
    "plv": {
        "enabled": True,
        "type": "functional",
        "description": "Phase Locking Value (PLV)",
    },
    "structural_dti": {
        "enabled": True,
        "type": "structural",
        "description": "DTI tractography streamline counts",
        "normalize": True,      # normalize by region volume
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# LAPLACIAN COMPUTATION
# ─────────────────────────────────────────────────────────────────────────────
LAPLACIAN = {
    "type": "combinatorial",    # L = D - A  (combinatorial Laplacian)
    # Alternatives: "normalized" (L_sym = D^-1/2 L D^-1/2), "random_walk"
    # Research plan specifies L = D - A
    "eigenvalue_method": "eigsh",  # scipy.sparse.linalg.eigsh
    "n_eigenvalues": "full",       # "full" = all, or integer for partial
    "which": "SM",                 # smallest magnitude (for full spectrum use "LM" ascending)
}

# ─────────────────────────────────────────────────────────────────────────────
# RESCALING PARAMETERS — λ₂ is PMIR prediction; others are comparison conditions
# ─────────────────────────────────────────────────────────────────────────────
RESCALING_METHODS = {
    "lambda2": {
        "enabled": True,
        "primary": True,           # PMIR prediction
        "description": "Rescale by λ₂ (algebraic connectivity)",
    },
    "lambda_max": {
        "enabled": True,
        "primary": False,          # Comparison condition
        "description": "Rescale by λ_max (spectral radius of Laplacian)",
    },
    "mean_eigenvalue": {
        "enabled": True,
        "primary": False,
        "description": "Rescale by mean eigenvalue",
    },
    "spectral_radius": {
        "enabled": True,
        "primary": False,
        "description": "Rescale by spectral radius of adjacency matrix",
    },
}
# Falsification criterion: if any alternative produces comparable collapse, λ₂ claim is weakened

# ─────────────────────────────────────────────────────────────────────────────
# NULL MODELS — 4 required by research plan
# ─────────────────────────────────────────────────────────────────────────────
NULL_MODELS = {
    "erdos_renyi": {
        "enabled": True,
        "description": "Erdős-Rényi random graphs with matched edge density",
        "n_samples": 100,
    },
    "degree_preserved": {
        "enabled": True,
        "description": "Degree-preserved random graphs (configuration model)",
        "n_samples": 100,
        "falsification_threshold": 0.90,
    },
    "strength_preserved": {
        "enabled": True,
        "description": "Strength-preserved random graphs (weighted configuration)",
        "n_samples": 100,
    },
    "geometric": {
        "enabled": False,          # Optional extension
        "description": "Random geometric graphs in 3D brain space",
        "n_samples": 500,
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# STATISTICAL TESTING
# ─────────────────────────────────────────────────────────────────────────────
STATISTICS = {
    "permutation_test_n": 1000,       # permutations for null distribution
    "significance_threshold": 0.001,   # p < 0.001 required
    "bonferroni_correction": True,
    "n_comparisons": 5,               # number of spectral bands tested
}

# ─────────────────────────────────────────────────────────────────────────────
# CONFIRMATION / FALSIFICATION THRESHOLDS (from research plan)
# ─────────────────────────────────────────────────────────────────────────────
THRESHOLDS = {
    # Confirmation
    "min_correlation_resting": 0.95,          # r > 0.95 in resting wakefulness
    "min_parcellations_confirmed": 3,          # must hold for 3+ parcellation schemes
    "max_null_model_correlation": 0.90,        # null models must stay below this

    # Falsification
    "falsification_null_model_r": 0.90,        # degree-preserved null > 0.90 → trivial
    "falsification_parcellation_floor": 0.80,  # if any parcellation drops below this → fail
    "consciousness_gradient_required": True,    # systematic degradation wake→sleep required
}

# ─────────────────────────────────────────────────────────────────────────────
# CONSCIOUSNESS STATE ORDERING (for gradient analysis)
# ─────────────────────────────────────────────────────────────────────────────
CONSCIOUSNESS_DEPTH_ORDER = [
    "wake",
    "light_sedation",
    "NREM1",
    "NREM2",
    "deep_sedation",
    "NREM3",
]
# Expected: universality (r) should monotonically decrease along this gradient

# ─────────────────────────────────────────────────────────────────────────────
# COMPUTATION SETTINGS
# ─────────────────────────────────────────────────────────────────────────────
COMPUTE = {
    "n_jobs": -1,          # -1 = use all CPU cores (joblib)
    "random_seed": 42,
    "cache_eigenspectra": True,   # save computed eigenspectra to avoid recomputation
    "cache_dir": os.path.join(DATA_DIR, "eigenspectra_cache"),
    "verbose": True,
}
