import pytest
import pandas as pd
import numpy as np
from agnipariksha.module_b.predictor import DriftPredictor
from agnipariksha.config import FAMILY_SPECS

def test_no_leakage():
    """Assert feature columns contain no >24h information."""
    predictor = DriftPredictor()
    
    # Create a dummy df with future columns
    df = pd.DataFrame({
        "value_0h": [10.0, 11.0],
        "value_24h": [12.0, 13.0],
        "value_96h": [14.0, 15.0],
        "value_168h": [16.0, 17.0]
    })
    
    # Call extract_features
    features = predictor.extract_features(df, current_hour=24)
    
    # Assert that no column in the returned features contains '96h' or '168h'
    for col in features.columns:
        assert "96h" not in col, f"LEAKAGE DETECTED: {col}"
        assert "168h" not in col, f"LEAKAGE DETECTED: {col}"

def test_safety_slope_trio():
    """
    (a) Y24=95% escalates before 168h.
    (b) sub-limit abnormal drift escalates.
    (c) normal drift does not.
    """
    predictor = DriftPredictor()
    family = "DIGITAL_IC"
    spec_max = FAMILY_SPECS[family]["spec_max"] # 50.0
    
    # Mocking predictor so pred_168h doesn't interfere randomly
    class MockPredictor(DriftPredictor):
        def predict_with_conformal(self, df, fam):
            res = pd.DataFrame(index=df.index)
            # Just assume it perfectly continues the measured slope
            slope = (df["value_24h"] - df["value_0h"]) / 24.0
            res["pred_168h"] = df["value_24h"] + slope * (168.0 - 24.0)
            res["conformal_radius_90"] = 0.0
            res["conformal_radius_95"] = 0.0
            return res
            
    predictor = MockPredictor()
    
    # Build a lot to establish lot statistics
    # Normal lot drift is from 10 to 10.1 over 24h. Slope = 0.1/24 = 0.0041
    n_normal = 50
    df_normal = pd.DataFrame({
        "family": [family] * n_normal,
        "value_0h": [10.0] * n_normal,
        "value_24h": [10.1] * n_normal
    })
    
    # (a) near-limit case: Y24 = 95% of spec (47.5)
    # 0h = 47.0, 24h = 47.5. Slope = 0.5/24 = 0.02.
    # Headroom bound = (50 - 47.5) / 144 = 2.5 / 144 = 0.017.
    # Measured slope 0.02 > Headroom bound 0.017. MUST ESCALATE!
    df_a = pd.DataFrame({
        "family": [family],
        "value_0h": [47.0],
        "value_24h": [47.5]
    })
    
    # (b) sub-limit abnormal drift:
    # 0h = 10.0, 24h = 20.0. Y24 is well below 50.
    # Slope = 10/24 = 0.41.
    # Relative bound = (0.10 * 50) / 168 = 5 / 168 = 0.029.
    # Measured slope 0.41 > Relative bound 0.029. MUST ESCALATE!
    df_b = pd.DataFrame({
        "family": [family],
        "value_0h": [10.0],
        "value_24h": [20.0]
    })
    
    # Combine to pass as a lot
    df_lot = pd.concat([df_normal, df_a, df_b], ignore_index=True)
    
    res = predictor.compute_safety_slope(df_lot, current_hour=24)
    
    # Normal parts
    assert res.loc[0, "module_b_verdict"] == "GREEN"
    
    # (a) near limit
    # The index in concat is 50.
    assert "RED" in res.loc[50, "module_b_verdict"]
    
    # (b) abnormal drift
    assert "RED" in res.loc[51, "module_b_verdict"]

def test_min_bound_binding():
    """Explicit unit test that the BINDING branch of min(headroom, relative) is reported."""
    predictor = DriftPredictor()
    # Mock
    class MockPredictor(DriftPredictor):
        def predict_with_conformal(self, df, fam):
            res = pd.DataFrame(index=df.index)
            res["pred_168h"] = df["value_24h"]
            res["conformal_radius_90"] = 0.0
            res["conformal_radius_95"] = 0.0
            return res
    predictor = MockPredictor()
    
    family = "DIGITAL_IC"
    
    # Case where Headroom < Relative
    # Y24 = 49.0. Spec = 50.
    # Headroom = 1.0 / 144 = 0.0069
    # Relative = 5.0 / 168 = 0.0297
    # Allowed should be Headroom.
    df_lot1 = pd.DataFrame({
        "family": [family, family],
        "value_0h": [49.0, 49.0],
        "value_24h": [49.0, 49.0]
    })
    res1 = predictor.compute_safety_slope(df_lot1, current_hour=24)
    assert np.isclose(res1.loc[0, "allowed_slope"], (50 - 49)/144)
    assert res1.loc[0, "allowed_slope"] < (5.0 / 168)
    
    # Case where Relative < Headroom
    # Y24 = 10.0. Spec = 50.
    # Headroom = 40.0 / 144 = 0.277
    # Relative = 5.0 / 168 = 0.0297
    # Allowed should be Relative.
    df_lot2 = pd.DataFrame({
        "family": [family, family],
        "value_0h": [10.0, 10.0],
        "value_24h": [10.0, 10.0]
    })
    res2 = predictor.compute_safety_slope(df_lot2, current_hour=24)
    assert np.isclose(res2.loc[0, "allowed_slope"], 5.0/168)
    assert res2.loc[0, "allowed_slope"] < (50 - 10)/144
