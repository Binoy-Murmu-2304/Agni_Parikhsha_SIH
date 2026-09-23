import os
with open('agnipariksha/api/main.py', 'r') as f:
    c = f.read()
c = c.replace("explanation={'feature_importance': {}}", "explanation={'feature_importance': {}, 'base_value': 0.0}")
with open('agnipariksha/api/main.py', 'w') as f:
    f.write(c)

with open('gen_cards.py', 'r') as f:
    c2 = f.read()
c2 = c2.replace("explanation={'feature_importance': {}}", "explanation={'feature_importance': {}, 'base_value': 0.0}")
with open('gen_cards.py', 'w') as f:
    f.write(c2)
