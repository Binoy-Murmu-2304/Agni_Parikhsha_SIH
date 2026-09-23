import os
import re

with open('agnipariksha/evaluation/evaluator.py', 'r') as f:
    c = f.read()

old_eval = "        def evaluate_disposition(row):\n            if row['final_flag'] == 1:\n                return 'RED'\n            if CAPABILITY_ROUTING.get(row['family']) == 'MANDATORY_FULL_BURN_IN':\n                return 'FULL_BURN_IN'\n            return 'GREEN'"

new_eval = "        def evaluate_disposition(row):\n            if CAPABILITY_ROUTING.get(row['family']) == 'MANDATORY_FULL_BURN_IN':\n                return 'FULL_BURN_IN'\n            if row['final_flag'] == 1:\n                return 'RED'\n            return 'GREEN'"

c = c.replace(old_eval, new_eval)
with open('agnipariksha/evaluation/evaluator.py', 'w') as f:
    f.write(c)

with open('agnipariksha/api/main.py', 'r') as f:
    c = f.read()

c = re.sub(r'    # API Doctrine: Enforce capability routing strictly\..*?df_res\[\'disposition\'\] = df_res\.apply\(enforce_api_routing, axis=1\)\n', '', c, flags=re.DOTALL)

with open('agnipariksha/api/main.py', 'w') as f:
    f.write(c)
