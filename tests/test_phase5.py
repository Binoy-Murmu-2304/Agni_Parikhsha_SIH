import pytest
import pandas as pd
import numpy as np
from agnipariksha.module_a.outlier import DynamicOutlierDetector
from agnipariksha.module_b.predictor import DriftPredictor
from agnipariksha.evaluation.evaluator import AgniEvaluator
from agnipariksha.evaluation.stress_tester import StressTester
from agnipariksha.config import FAMILY_SPECS

def test_fn_penalized_score():
    evaluator = AgniEvaluator(w_fn=50, w_fp=1)
    
    # Perfect score
    assert evaluator.calculate_score(fp=0, fn=0, n_total=100) == 100.0
    
    # One false positive
    assert evaluator.calculate_score(fp=1, fn=0, n_total=100) == 99.0
    
    # One false negative (huge penalty)
    assert evaluator.calculate_score(fp=0, fn=1, n_total=100) == 50.0
    
    # Floor at 0
    assert evaluator.calculate_score(fp=0, fn=3, n_total=100) == 0.0

def test_conformal_coverage_computation():
    evaluator = AgniEvaluator()
    predictor = DriftPredictor()
    
    family = "DIGITAL_IC"
    
    # Mock predictor
    class MockPredictor(DriftPredictor):
        def predict_with_conformal(self, df, fam):
            res = pd.DataFrame(index=df.index)
            # Perfect predictions
            res["pred_168h"] = df["value_168h"]
            res["conformal_radius_90"] = 0.5
            res["conformal_radius_95"] = 0.6
            return res
            
    mock_pred = MockPredictor()
    
    df_blind = pd.DataFrame({
        "family": [family]*100,
        "value_0h": [10]*100,
        "value_24h": [11]*100,
        "value_168h": [12]*100
    })
    
    metrics = evaluator.conformal_coverage_audit(df_blind, mock_pred)
    
    # Because predictions are perfect and radius > 0, coverage should be 100%
    assert metrics[family]["cov_90"] == 1.0
    assert metrics[family]["cov_95"] == 1.0
    # Rule of three or exact clopper pearson should give a tight upper bound, lower bound > 0.95
    assert metrics[family]["cov_90_CI"][0] > 0.95
    assert metrics[family]["n"] == 100

def test_mae_guard_behavior():
    from agnipariksha.evaluation.evaluator import AgniEvaluator
    from agnipariksha.module_a.outlier import DynamicOutlierDetector
    from agnipariksha.module_b.predictor import DriftPredictor
    import pandas as pd
    
    # Pristine failing-family component
    df_failing = pd.DataFrame({
        'lot_id': ['L_FAIL'],
        'component_id': ['C_FAIL'],
        'family': ['DIGITAL_IC'],
        'mechanism': ['NONE'],
        'value_0h': [10.0],
        'value_24h': [10.1],
        'is_defective': [0]
    })
    
    # Passing-family clean component
    df_passing = pd.DataFrame({
        'lot_id': ['L_PASS'],
        'component_id': ['C_PASS'],
        'family': ['MEMS_GYROSCOPE'],
        'mechanism': ['NONE'],
        'value_0h': [0.1],
        'value_24h': [0.101],
        'is_defective': [0]
    })
    
    mod_a = DynamicOutlierDetector()
    mod_b = DriftPredictor()
    evaluator = AgniEvaluator()
    
    res_fail = evaluator.end_to_end_disposition(df_failing, mod_a, mod_b, k_noise=0.0)
    res_pass = evaluator.end_to_end_disposition(df_passing, mod_a, mod_b, k_noise=0.0)
    
    assert res_fail['disposition'].iloc[0] == 'FULL_BURN_IN', "Failing family should not emit GREEN"
    assert res_pass['disposition'].iloc[0] == 'GREEN', "Passing family clean component should emit GREEN"

def test_min_branch_behavior():
    from agnipariksha.module_b.predictor import DriftPredictor
    import pandas as pd
    mod_b = DriftPredictor()
    df_dummy = pd.DataFrame({
        'family': ['DIGITAL_IC'],
        'value_0h': [0.1],
        'value_24h': [48.0]
    })
    df_res = mod_b.compute_safety_slope(df_dummy, current_hour=24, k_noise=0.0)
    assert abs(df_res['allowed_slope'].iloc[0] - 0.0138) <= 0.002
