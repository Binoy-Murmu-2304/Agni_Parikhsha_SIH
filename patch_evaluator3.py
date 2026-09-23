import os

with open('agnipariksha/evaluation/evaluator.py', 'r') as f:
    content = f.read()

replacement = '''
                fam = lot_data['family'].iloc[0]
                df_neg_pool = lot_data[lot_data['is_defective'] == 0]
                
                n_neg = len(df_neg_pool)
                n_def = int(round(n_neg * rate / (1 - rate)))
                n_total = n_neg + n_def
                
                df_neg = df_neg_pool # use all healthy parts in the lot
                
                df_fam_pool = df_population[df_population['family'] == fam]
                df_def_pool = df_fam_pool[df_fam_pool['is_defective'] == 1]
                if len(df_def_pool) < n_def:
                    raise ValueError(f"Insufficient defectives in family {fam}")
                df_def = df_def_pool.sample(n=n_def, random_state=42)
'''

# Find the loop body
old_body = '''
                fam = lot_data['family'].iloc[0]
                n_total = len(lot_data)
                n_def = int(n_total * rate)
                n_neg = n_total - n_def
                
                # sample healthy from the lot
                df_neg_pool = lot_data[lot_data['is_defective'] == 0]
                if len(df_neg_pool) < n_neg:
                    raise ValueError(f"Insufficient healthy in lot {lot_id}")
                df_neg = df_neg_pool.sample(n=n_neg)
                
                # sample defectives from the whole family in df_population to simulate injection
                df_fam_pool = df_population[df_population['family'] == fam]
                df_def_pool = df_fam_pool[df_fam_pool['is_defective'] == 1]
                if len(df_def_pool) < n_def:
                    raise ValueError(f"Insufficient defectives in family {fam}")
                df_def = df_def_pool.sample(n=n_def)
'''

content = content.replace(old_body.strip(), replacement.strip())
with open('agnipariksha/evaluation/evaluator.py', 'w') as f:
    f.write(content)
