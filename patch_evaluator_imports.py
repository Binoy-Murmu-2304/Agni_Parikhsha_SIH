import os

with open('agnipariksha/evaluation/evaluator.py', 'r') as f:
    content = f.read()

content = content.replace(
    'from agnipariksha.config import FAMILY_SPECS, DEFAULT_W_FN',
    'from agnipariksha.config import FAMILY_SPECS, DEFAULT_W_FN, CAPABILITY_ROUTING'
)

with open('agnipariksha/evaluation/evaluator.py', 'w') as f:
    f.write(content)
