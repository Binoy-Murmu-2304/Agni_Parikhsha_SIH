import os
with open('run_final_eval.py', 'r') as f:
    c = f.read()
c = c.replace('df_combined.to_markdown(index=False)', 'df_combined.to_string(index=False)')
with open('run_final_eval.py', 'w') as f:
    f.write(c)
