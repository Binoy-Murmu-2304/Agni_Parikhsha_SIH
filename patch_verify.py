import os

with open('agnipariksha/evaluation/verify_claims.py', 'r') as f:
    c = f.read()

c = c.replace('Realized Chamber Savings (B3 formulation at 5.0% prev):', 'Realized Chamber Savings (5% defect injection mix on healthy pool (?2.9% effective)):')

with open('agnipariksha/evaluation/verify_claims.py', 'w') as f:
    f.write(c)
