import os
with open('docs/FINAL_EVAL_REPORT.md', 'r') as f:
    c = f.read()
c = c.replace('[95% CI: 22.89%, 32.17%]', '[95% Clopper-Pearson CI: 22.95%, 32.48%]')
with open('docs/FINAL_EVAL_REPORT.md', 'w') as f:
    f.write(c)

