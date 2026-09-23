import pytest
import pandas as pd
import numpy as np
from agnipariksha.module_a.outlier import DynamicOutlierDetector
from agnipariksha.config import MODULE_A_MIN_LOT_SIZE

def test_canonical_ps_scenario():
    """
    Test Phase 2.4: 
    lot with mean 10 µA, one part at 45 µA, datasheet max 50 µA
    -> must be flagged as a dynamic anomaly at 24h despite passing static limits.
    """
    # Create lot where median is ~10 and MAD is small (e.g. 1)
    vals = np.random.normal(10, 1.4826, 100) # std dev is 1.4826 so MAD is approx 1.0
    vals[0] = 45.0 # The outlier part
    
    df = pd.DataFrame({"component_id": [f"c_{i}" for i in range(100)], "value_24h": vals})
    
    detector = DynamicOutlierDetector(z_yellow=3.5, z_red=5.0)
    result_df = detector.detect_univariate(df, "value_24h")
    
    # Check the outlier part
    outlier_verdict = result_df.loc[0, "module_a_verdict"]
    outlier_z = result_df.loc[0, "module_a_z_score"]
    
    # 45 is way above median 10 with MAD 1. Z > 20. Should be RED.
    assert outlier_verdict == "RED"
    assert outlier_z > 5.0
    
    # Check a normal part
    normal_verdict = result_df.loc[1, "module_a_verdict"]
    assert normal_verdict == "GREEN"

def test_lot_adaptivity():
    """
    Test lot-adaptivity: same absolute value into two lots gets different verdicts.
    """
    detector = DynamicOutlierDetector(z_yellow=3.5, z_red=5.0)
    
    # Lot A: tightly centered around 10
    lot_a_vals = np.random.normal(10, 1.0, 50)
    lot_a_vals[0] = 20.0 # Test value
    df_a = pd.DataFrame({"value_24h": lot_a_vals})
    res_a = detector.detect_univariate(df_a, "value_24h")
    
    # Lot B: widely spread around 20
    lot_b_vals = np.random.normal(20, 5.0, 50)
    lot_b_vals[0] = 20.0 # Same test value
    df_b = pd.DataFrame({"value_24h": lot_b_vals})
    res_b = detector.detect_univariate(df_b, "value_24h")
    
    # Value 20 in Lot A is 10 standard deviations away -> RED
    assert res_a.loc[0, "module_a_verdict"] == "RED"
    
    # Value 20 in Lot B is exactly the median -> GREEN
    assert res_b.loc[0, "module_a_verdict"] == "GREEN"

def test_tiny_lot_guard():
    """
    Test small lot guard (n < MODULE_A_MIN_LOT_SIZE -> FULL_BURN_IN)
    """
    detector = DynamicOutlierDetector()
    df = pd.DataFrame({"value_24h": [10, 11, 10]}) # n=3
    assert len(df) < MODULE_A_MIN_LOT_SIZE
    
    res = detector.detect_univariate(df, "value_24h")
    assert (res["module_a_verdict"] == "FULL_BURN_IN").all()

def test_mad_zero_guard():
    """
    Test MAD = 0 scenario (all values identical). Should not divide by zero.
    """
    detector = DynamicOutlierDetector()
    df = pd.DataFrame({"value_24h": [10.0] * 50})
    df.loc[0, "value_24h"] = 10.1 # Slight deviation
    
    res = detector.detect_univariate(df, "value_24h")
    assert not np.isnan(res["module_a_z_score"]).any()
    assert not np.isinf(res["module_a_z_score"]).any()
    # The slight deviation might trigger an outlier if the floor is very small.
    # We just care it doesn't crash or return NaN.
