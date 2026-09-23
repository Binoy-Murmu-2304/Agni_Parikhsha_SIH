import os

with open('agnipariksha/evaluation/evaluator.py', 'r') as f:
    content = f.read()

replacement = '''
                df_def = df_def_pool.sample(n=n_def, random_state=42 + int(str(lot_id).split('_')[-1]))
                
                df_eval = pd.concat([df_def, df_neg]).reset_index(drop=True)
                assert len(df_eval['component_id'].unique()) == len(df_eval), "Duplicate component_ids in evaluation frame!"
'''

old = '''
                df_def = df_def_pool.sample(n=n_def, random_state=42)
                
                df_eval = pd.concat([df_def, df_neg]).reset_index(drop=True)
'''

content = content.replace(old.strip(), replacement.strip())

with open('agnipariksha/evaluation/evaluator.py', 'w') as f:
    f.write(content)
