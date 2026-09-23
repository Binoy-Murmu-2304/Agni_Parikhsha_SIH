import pandas as pd
import json
from agnipariksha.config import FAMILY_SPECS
from agnipariksha.module_a.outlier import DynamicOutlierDetector
from agnipariksha.module_b.predictor import DriftPredictor
from agnipariksha.evaluation.evaluator import AgniEvaluator

df_main = pd.read_csv("data/dataset.csv")
with open("data/manifest.json", "r") as f: manifest = json.load(f)

train_lots = [item['lot_id'] for item in manifest['TRAIN']]
cal_lots = [item['lot_id'] for item in manifest['CALIBRATION']]
dev_lots = [item['lot_id'] for item in manifest['DEVELOPMENT']]
final_lots = [item['lot_id'] for item in manifest['FINAL_EVAL']]  # Actually called BLIND_TEST in manifest

df_train = df_main[df_main['lot_id'].isin(train_lots)]
df_cal = df_main[df_main['lot_id'].isin(cal_lots)]
df_dev = df_main[df_main['lot_id'].isin(dev_lots)]
df_final = df_main[df_main['lot_id'].isin(final_lots)]

module_b = DriftPredictor()
module_b.fit(df_train, df_cal)
module_a = DynamicOutlierDetector()
evaluator = AgniEvaluator()

df_prev_dev = evaluator.evaluate_prevalence(df_dev, module_a, module_b, prevalence_rates=[0.005, 0.05], k_noise=3.5)
df_prev_dev['Provenance'] = 'DEVELOPMENT'

df_prev_final = evaluator.evaluate_prevalence(df_final, module_a, module_b, prevalence_rates=[0.005, 0.05], k_noise=3.5)
df_prev_final['Provenance'] = 'FINAL_EVAL'

df_combined = pd.concat([df_prev_dev, df_prev_final], ignore_index=True)

# Also let's compute B3 realized savings for FINAL_EVAL
with open('metrics_canonical.json', 'r') as mf:
    canonical = json.load(mf)
failed = [fam for fam in FAMILY_SPECS.keys() if canonical.get(fam, {}).get('MAE', 0) / FAMILY_SPECS[fam]['spec_max'] > 0.20]

realized_savings = 0.0
share_f = 1 / len(FAMILY_SPECS)
chamber_savings = 85.71428571428571
for fam in FAMILY_SPECS.keys():
    if fam in failed:
        exit_rate = 0.0
    else:
        df_fam = df_final[df_final['family'] == fam]
        if len(df_fam) == 0:
            continue
        n_def = 100
        df_neg = df_fam[df_fam['is_defective'] == 0]
        # We need to sample carefully for FINAL_EVAL just like we do.
        df_def = df_fam[df_fam['is_defective'] == 1]
        if len(df_def) > n_def:
            df_def = df_def.sample(n=n_def, random_state=42)
        df_eval = pd.concat([df_def, df_neg])
        df_res = evaluator.end_to_end_disposition(df_eval, module_a, module_b, k_noise=3.5)
        exit_rate = 1.0 - df_res['final_flag'].mean()
    realized_savings += share_f * exit_rate * chamber_savings

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

with open('docs/FINAL_EVAL_REPORT.md', 'w') as f:
    f.write("# FINAL EVALUATION REPORT\n\n")
    f.write("## Prevalence Sweep (DEVELOPMENT vs FINAL_EVAL)\n")
    f.write(df_combined.to_string(index=False))
    f.write(f"\n\n## Realized Chamber Savings (FINAL_EVAL)\n")
    f.write(f"Computed B3 Exit Rates on FINAL_EVAL: **{realized_savings:.2f}%**\n")

print(df_combined)
print(f"Realized Chamber Savings (FINAL_EVAL): {realized_savings:.2f}%")
