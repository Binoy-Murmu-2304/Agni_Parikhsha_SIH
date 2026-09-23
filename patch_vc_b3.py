import os

with open('append_vc2.py', 'r') as f:
    content = f.read()

replacement = '''
                n_def = 100
                df_neg = df_fam[df_fam['is_defective'] == 0]
                df_def = df_fam[df_fam['is_defective'] == 1].sample(n=n_def, random_state=42)
'''

old = '''
                n_def = 100
                n_neg = 1900
                df_def = df_fam[df_fam['is_defective'] == 1].sample(n=n_def, random_state=42)
                df_neg = df_fam[df_fam['is_defective'] == 0].sample(n=n_neg, random_state=42)
'''

content = content.replace(old.strip(), replacement.strip())
with open('append_vc2.py', 'w') as f:
    f.write(content)
