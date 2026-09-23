import os
with open('run_final_eval.py', 'r') as f:
    c = f.read()
c = c.replace("'BLIND_TEST'", "'FINAL_EVAL'")
with open('run_final_eval.py', 'w') as f:
    f.write(c)
