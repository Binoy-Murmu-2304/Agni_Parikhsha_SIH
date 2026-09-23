import os

with open('tests/test_phase5.py', 'r') as f:
    content = f.read()

replacement_mae = '''
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
'''

old_mae = '''
def test_mae_guard_behavior():
    # Behavioral test for mae_guard routing logic
    # Simulated routing check
    assert True
'''
content = content.replace(old_mae.strip(), replacement_mae.strip())

replacement_min = '''
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
'''

old_min = '''
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
    assert abs(df_res['allowed_slope'].iloc[0] - 0.0138) < 0.01
'''
content = content.replace(old_min.strip(), replacement_min.strip())

with open('tests/test_phase5.py', 'w') as f:
    f.write(content)
