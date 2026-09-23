import os

with open('agnipariksha/evaluation/verify_claims.py', 'r') as f:
    content = f.read()

# We need to replace the static failed families array in B3 with dynamic ones.
# Also we need to rename B3 prevalence to 5.0%.
replacement = '''
        import json
        with open('metrics_canonical.json', 'r') as mf:
            canonical = json.load(mf)
            
        failed = [fam for fam in FAMILY_SPECS.keys() if canonical.get(fam, {}).get('MAE', 0) / FAMILY_SPECS[fam]['spec_max'] > 0.20]
        
        realized_savings = 0.0
        share_f = 1 / len(FAMILY_SPECS)
        for fam in FAMILY_SPECS.keys():
            if fam in failed:
                exit_rate = 0.0
            else:
                df_fam = df_blind[df_blind['family'] == fam]
                n_def = 100
                df_neg = df_fam[df_fam['is_defective'] == 0]
                df_def = df_fam[df_fam['is_defective'] == 1].sample(n=n_def, random_state=42)
                df_eval = pd.concat([df_def, df_neg])
                df_res = evaluator.end_to_end_disposition(df_eval, module_a, module_b, k_noise=3.5)
                exit_rate = 1.0 - df_res['final_flag'].mean()
            realized_savings += share_f * exit_rate * chamber_savings
        
        print(f"Realized Chamber Savings (B3 formulation at 5.0% prev): {realized_savings:.2f}%")
'''

old = '''
        failed = ['DIGITAL_IC', 'MIXED_SIGNAL_IC', 'PRECISION_VOLTAGE_REF']
        realized_savings = 0.0
        share_f = 1 / len(FAMILY_SPECS)
        for fam in FAMILY_SPECS.keys():
            if fam in failed:
                exit_rate = 0.0
            else:
                df_fam = df_blind[df_blind['family'] == fam]
                n_def = 100
                df_neg = df_fam[df_fam['is_defective'] == 0]
                df_def = df_fam[df_fam['is_defective'] == 1].sample(n=n_def, random_state=42)
                df_eval = pd.concat([df_def, df_neg])
                df_res = evaluator.end_to_end_disposition(df_eval, module_a, module_b, k_noise=3.5)
                exit_rate = 1.0 - df_res['final_flag'].mean()
            realized_savings += share_f * exit_rate * chamber_savings
        
        print(f"Realized Chamber Savings (B3 formulation at 5% prev): {realized_savings:.2f}%")
'''

content = content.replace(old.strip(), replacement.strip())
with open('agnipariksha/evaluation/verify_claims.py', 'w') as f:
    f.write(content)
