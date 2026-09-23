import os

with open('dashboard/pages/index.js', 'r', encoding='utf-8') as f:
    c = f.read()

# I will add the conformal bug limitation explicitly
new_limitation = '''                <p><strong>Conformal Trigger:</strong> Excluded from final_flag as a design decision (the prior claim of "0 detections on AGNI-SIM" was a bug artifact).</p>'''

if 'Conformal Under-coverage' in c:
    c = c.replace('<p><strong>Conformal Under-coverage:', new_limitation + '\n                <p><strong>Conformal Under-coverage:')

with open('dashboard/pages/index.js', 'w', encoding='utf-8') as f:
    f.write(c)

with open('fixes/CLAIM_HISTORY.md', 'a', encoding='utf-8') as f:
    f.write("\n- Conformal-breach trigger: the recorded '0%/0% firing on AGNI-SIM' was a BUG ARTIFACT ? predictor.py dropped conformal_radius columns on return, so evaluator.py's conformal_breach check silently read missing values and never fired. Columns restored (2026-09-23). Trigger remains EXCLUDED from final_flag as a design decision. The prior justification ('0 detections on AGNI-SIM', 'stripped as dead') is RETRACTED as a bug artifact.\n")
