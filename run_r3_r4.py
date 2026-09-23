import pandas as pd
import json
import numpy as np
import scipy.stats as stats
from agnipariksha.config import FAMILY_SPECS

df_main = pd.read_csv("data/dataset.csv")
with open("data/manifest.json", "r") as f: manifest = json.load(f)
df_blind = df_main[df_main['lot_id'].isin([item['lot_id'] for item in manifest['BLIND_TEST']])]

from agnipariksha.module_b.predictor import DriftPredictor
df_train = df_main[df_main['lot_id'].isin([item['lot_id'] for item in manifest['TRAIN']])]
df_cal = df_main[df_main['lot_id'].isin([item['lot_id'] for item in manifest['CALIBRATION']])]
module_b = DriftPredictor()
module_b.fit(df_train, df_cal)

df_preds = df_blind.copy()
for fam in df_blind['family'].unique():
    df_f = df_blind[df_blind['family'] == fam]
    p = module_b.predict_with_conformal(df_f, fam)
    df_preds.loc[df_f.index, 'pred_168h'] = p['pred_168h']
    df_preds.loc[df_f.index, 'conformal_radius_90'] = p['conformal_radius_90']

def proportion_confint(k, n, alpha=0.10):
    lower = stats.beta.ppf(alpha/2, k, n - k + 1) if k > 0 else 0
    upper = stats.beta.ppf(1 - alpha/2, k + 1, n - k) if k < n else 1
    return lower, upper

print("=== R3: HONEST CONFORMAL REPORTING ===")
for fam in df_preds['family'].unique():
    df_f = df_preds[df_preds['family'] == fam]
    err = np.abs(df_f['value_168h'] - df_f['pred_168h'])
    
    # 90%
    cov_90 = (err <= df_f['conformal_radius_90']).mean()
    n = len(df_f)
    k = int(cov_90 * n)
    ci_90 = proportion_confint(k, n, alpha=0.10)
    status_90 = "PASS" if ci_90[0] <= 0.90 <= ci_90[1] else f"UNDERCOVERAGE (Exchangeability violation)"
    print(f"{fam} 90%: {cov_90*100:.1f}% CI: [{ci_90[0]*100:.1f}%, {ci_90[1]*100:.1f}%] -> {status_90}")
    
print("\n=== R4: FAMILY CAPABILITY AUDIT ===")
for fam in df_preds['family'].unique():
    df_f = df_preds[df_preds['family'] == fam]
    spec = FAMILY_SPECS[fam]['spec_max']
    df_h = df_f[df_f['is_defective'] == 0]
    df_d = df_f[df_f['is_defective'] == 1]
    
    mae_h = np.abs(df_h['value_168h'] - df_h['pred_168h']).mean()
    mae_d = np.abs(df_d['value_168h'] - df_d['pred_168h']).mean()
    mae_all = np.abs(df_f['value_168h'] - df_f['pred_168h']).mean()
    
    ratio = mae_all / spec
    verdict = "GREEN AUTO-PASS ALLOWED" if ratio <= 0.20 else "MANDATORY FULL BURN-IN (MAE > 20% spec)"
    
    print(f"{fam}: MAE={mae_all:.2f} (H:{mae_h:.2f}, D:{mae_d:.2f}) | Spec={spec} | Ratio={ratio*100:.1f}% | {verdict}")

