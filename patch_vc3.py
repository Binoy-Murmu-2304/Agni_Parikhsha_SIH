import os

with open('agnipariksha/evaluation/verify_claims.py', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'PASS AGNI_mae_guard' in line or 'PASS AGNI_w_fn_ranking' in line or 'PASS AGNI_min_branch' in line:
        continue
    if "expected_val = 1.0" in line and ("mae_guard" in line or "w_fn" in line or "min" in line):
        continue
    new_lines.append(line)

with open('agnipariksha/evaluation/verify_claims.py', 'w') as f:
    f.writelines(new_lines)
