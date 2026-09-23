def test_safety_slope_noise_tolerance():
    from agnipariksha.module_b.predictor import DriftPredictor
    from agnipariksha.config import FAMILY_SPECS
    import pandas as pd
    import numpy as np

    family = 'DIGITAL_IC'
    spec_max = FAMILY_SPECS[family]['spec_max']
    
    class MockPredictor(DriftPredictor):
        def predict_with_conformal(self, df, fam):
            res = pd.DataFrame(index=df.index)
            res['pred_168h'] = df['value_24h']
            res['conformal_radius_90'] = 0.0
            res['conformal_radius_95'] = 0.0
            return res
            
    predictor = MockPredictor()
    
    # Noise generation
    n_normal = 100
    df_normal = pd.DataFrame({
        "family": [family] * n_normal,
        "value_0h": [10.0] * n_normal,
        "value_24h": [10.0] * n_normal
    })
    
    # (d) healthy part at max realistic measurement noise must NOT escalate
    # relative bound = 0.1 * 50 / 168 = 0.0297
    # we inject a part with measured_slope = 0.035 > allowed_slope
    df_normal.loc[0, 'value_24h'] = 10.0 + 24 * 0.035
    # we inject a lot of small noise to create mad_slope
    noise_slope = np.random.normal(0, 0.02, n_normal-2)
    df_normal.loc[2:, 'value_24h'] = df_normal.loc[2:, 'value_0h'] + noise_slope * 24
    
    # (e) defect drift at the minimum detectable effect still escalates
    # something well above lot stat bound and slope_tolerance
    df_normal.loc[1, 'value_24h'] = 10.0 + 24 * 0.15
    
    df_res = predictor.compute_safety_slope(df_normal, current_hour=24)
    
    # Part 0 should be GREEN because slope_tolerance saves it
    assert df_res.loc[0, 'module_b_verdict'] == 'GREEN', f"Failed (d): expected GREEN, got {df_res.loc[0, 'module_b_verdict']}"
    
    # Part 1 should be RED
    assert df_res.loc[1, 'module_b_verdict'] == 'RED_SAFETY_SLOPE', "Failed (e): expected RED"
