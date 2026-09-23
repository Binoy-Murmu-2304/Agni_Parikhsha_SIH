import os

with open('agnipariksha/evaluation/evaluator.py', 'r') as f:
    content = f.read()

replacement = '''
from ..config import FAMILY_SPECS, DEFAULT_W_FN, CAPABILITY_ROUTING

class AgniEvaluator:
'''

if "CAPABILITY_ROUTING" not in content:
    content = content.replace("from ..config import FAMILY_SPECS, DEFAULT_W_FN", replacement.strip())

replacement2 = '''
        def evaluate_final(row):
            if row['trigger_module_a'] == 1: return 1
            if row['trigger_safety_slope'] == 1: return 1
            return 0
            
        def evaluate_disposition(row):
            if row['final_flag'] == 1:
                return 'RED'
            if CAPABILITY_ROUTING.get(row['family']) == 'MANDATORY_FULL_BURN_IN':
                return 'FULL_BURN_IN'
            return 'GREEN'
            
        df_b['final_flag'] = df_b.apply(evaluate_final, axis=1)
        df_b['disposition'] = df_b.apply(evaluate_disposition, axis=1)
        return df_b
'''

old2 = '''
        def evaluate_final(row):
            if row['trigger_module_a'] == 1: return 1
            if row['trigger_safety_slope'] == 1: return 1
            # ConfBreach fires 0%, removed from final_flag as per F4
            return 0
            
        df_b['final_flag'] = df_b.apply(evaluate_final, axis=1)
        return df_b
'''

if "evaluate_disposition" not in content:
    content = content.replace(old2.strip(), replacement2.strip())

with open('agnipariksha/evaluation/evaluator.py', 'w') as f:
    f.write(content)
