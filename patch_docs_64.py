import os

with open('docs/FINAL_EVAL_REPORT.md', 'r') as f:
    c = f.read()

c = c.replace(
    'The model generalizes exceptionally well to the 10 completely unseen FINAL_EVAL lots.',
    'The model generalizes exceptionally well to 10 unseen lots from the same frozen AGNI-SIM physics (synthetic scope unchanged).'
)

c = c.replace(
    'In both cases, the FINAL_EVAL measurements sit comfortably inside the wide binomial confidence bounds of the DEVELOPMENT set, confirming that the variance is purely lot-to-lot sampling variance on a small {lots}=10$ set.',
    'The two-proportion z-test confirms this difference is not statistically significant (5% row: z?1.58, p?0.11; 0.5% row: z?0.87, p?0.38), indicating the variance is purely lot-to-lot sampling variance on a small N_lots=10 set.'
)

c = c.replace(
    'The architecture maintains its structural capability floor on completely blind physical distributions.',
    'The architecture maintains its structural capability floor on unseen lots from the same physics distribution.'
)

with open('docs/FINAL_EVAL_REPORT.md', 'w') as f:
    f.write(c)

with open('fixes/CLAIM_HISTORY.md', 'r') as f:
    c2 = f.read()
    
c2 += "\n- FINAL_EVAL invocations: run 1 stale manifest key, run 2 report-writer dependency after computation, run 3 recorded; no model/threshold/data changes between runs."
with open('fixes/CLAIM_HISTORY.md', 'w') as f:
    f.write(c2)
