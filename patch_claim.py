import os

with open('fixes/CLAIM_HISTORY.md', 'r') as f:
    content = f.read()

content = content.replace("Recall shifted from 70.45% to 74.07% at the identical shipped point.", "FPR shifted from an artificial 70.45% (under 0.0001 generator noise) down to 0.11% on DEVELOPMENT.")

with open('fixes/CLAIM_HISTORY.md', 'w') as f:
    f.write(content)
