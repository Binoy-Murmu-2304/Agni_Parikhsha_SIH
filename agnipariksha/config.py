"""
Single Source of Truth for AGNI PARIKSHA thresholds, seeds, and specification limits.
"""

# Global single SEED
SEED = 42

# Component Families and Specifications
# D3: PER-FAMILY METRICS ONLY for quantities with physical units
FAMILY_SPECS = {
    "DIGITAL_IC": {
        "unit": "µA",
        "spec_max": 50.0,
        "description": "Iddq standby leakage"
    },
    "MIXED_SIGNAL_IC": {
        "unit": "µA",
        "spec_max": 75.0,
        "description": "Leakage current"
    },
    "MEMS_GYROSCOPE": {
        "unit": "dps",
        "spec_max": 0.5,
        "description": "Bias drift rate"
    },
    "PRECISION_VOLTAGE_REF": {
        "unit": "µV",
        "spec_max": 100.0,
        "description": "Drift"
    },
    "IMAGE_SENSOR": {
        "unit": "nA/cm²",
        "spec_max": 10.0,
        "description": "Dark current"
    }
}

# Module A: Dynamic Outlier Detection Constants
MODULE_A_MIN_LOT_SIZE = 5

# Module B: Drift Predictor + Safety Slope Constants
# Safety slope definition constants
SAFETY_SLOPE_K_REL = 0.10  # 10% of spec range over full life
SAFETY_SLOPE_K_ROB = 3.5   # Consistent with robust Z

# Explainer / Scoring
FN_PENALTY_WEIGHT = 50  # 1 escaped space-grade defect ≈ 50 scrapped good parts
