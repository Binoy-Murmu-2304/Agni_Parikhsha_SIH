import os

with open('agnipariksha/evaluation/verify_claims.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('(?2.9% effective)', '(approx 2.9% effective)')
c = c.replace('?', 'approx ') # just in case

with open('agnipariksha/evaluation/verify_claims.py', 'w', encoding='utf-8') as f:
    f.write(c)

with open('docs/BUILD_REPORT.md', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('strictly map top component features to underlying physics', 'top SHAP features reported under real names with family-prior mechanism hypotheses (hedged)')
with open('docs/BUILD_REPORT.md', 'w', encoding='utf-8') as f:
    f.write(c)
