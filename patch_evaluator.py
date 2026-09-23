import os

with open('agnipariksha/evaluation/evaluator.py', 'r') as f:
    content = f.read()

content = content.replace('from ..config import FAMILY_SPECS', 'from ..config import FAMILY_SPECS, DEFAULT_W_FN')
content = content.replace('def __init__(self, w_fp: float = 1.0, w_fn: float = 10.0):', 'def __init__(self, w_fp: float = 1.0, w_fn: float = DEFAULT_W_FN):')
content = content.replace('if len(df_def) < n_def: df_def = df_def.sample(n=n_def, replace=True)', 'if len(df_def) < n_def: raise ValueError(f"Insufficient defectives for rate {rate} in {fam}")\n                else: df_def = df_def.sample(n=n_def)')
content = content.replace('if len(df_neg) < n_neg: df_neg = df_neg.sample(n=n_neg, replace=True)', 'if len(df_neg) < n_neg: raise ValueError(f"Insufficient healthy for rate {rate} in {fam}")\n                else: df_neg = df_neg.sample(n=n_neg)')

with open('agnipariksha/evaluation/evaluator.py', 'w') as f:
    f.write(content)

print("Updated evaluator.py")
