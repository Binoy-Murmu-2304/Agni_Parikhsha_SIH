import pandas as pd
import json
import numpy as np
from agnipariksha.config import FAMILY_SPECS
from agnipariksha.module_a.outlier import DynamicOutlierDetector
from agnipariksha.module_b.predictor import DriftPredictor
from agnipariksha.evaluation.evaluator import AgniEvaluator

# Load Data
df_main = pd.read_csv("data/dataset.csv")
with open("data/manifest.json", "r") as f: manifest = json.load(f)
train_lots = [item['lot_id'] for item in manifest['TRAIN']]
cal_lots = [item['lot_id'] for item in manifest['CALIBRATION']]
dev_lots = [item['lot_id'] for item in manifest['DEVELOPMENT']]
df_train = df_main[df_main['lot_id'].isin(train_lots)]
df_cal = df_main[df_main['lot_id'].isin(cal_lots)]
df_dev = df_main[df_main['lot_id'].isin(dev_lots)]

module_b = DriftPredictor()
module_b.fit(df_train, df_cal)
module_a = DynamicOutlierDetector()
evaluator = AgniEvaluator()

def eval_split(df_split):
    dfs_res = []
    for lot_id, lot_data in df_split.groupby("lot_id"):
        dfs_res.append(evaluator.end_to_end_disposition(lot_data, module_a, module_b, k_noise=3.5))
    return pd.concat(dfs_res)

df_cal_eval = eval_split(df_cal)
df_dev_eval = eval_split(df_dev)

def compute_metrics(df_eval):
    df_h = df_eval[df_eval['is_defective'] == 0]
    df_d = df_eval[df_eval['is_defective'] == 1]
    
    fpr = df_h['final_flag'].mean()
    recall = df_d['final_flag'].mean()
    
    mod_a_h = df_h['trigger_module_a'].mean()
    safe_h = df_h['trigger_safety_slope'].mean()
    lot_stat_h = df_h['trigger_lot_stat'].mean()
    conf_h = df_h['trigger_conformal'].mean()
    
    mod_a_d = df_d['trigger_module_a'].mean()
    safe_d = df_d['trigger_safety_slope'].mean()
    lot_stat_d = df_d['trigger_lot_stat'].mean()
    conf_d = df_d['trigger_conformal'].mean()
    
    return fpr, recall, mod_a_h, safe_h, lot_stat_h, conf_h, mod_a_d, safe_d, lot_stat_d, conf_d

cal_mets = compute_metrics(df_cal_eval)
dev_mets = compute_metrics(df_dev_eval)

print("=== B1: ONE CODE PATH, ONE TABLE ===")
print("Split | FPR | Recall | ModA (H/D) | SafeSlope (H/D) | LotStat (H/D) | ConfBreach (H/D)")
print(f"CALIBRATION | {cal_mets[0]*100:.2f}% | {cal_mets[1]*100:.2f}% | {cal_mets[2]*100:.1f}%/{cal_mets[6]*100:.1f}% | {cal_mets[3]*100:.2f}%/{cal_mets[7]*100:.1f}% | {cal_mets[4]*100:.1f}%/{cal_mets[8]*100:.1f}% | {cal_mets[5]*100:.1f}%/{cal_mets[9]*100:.1f}%")
print(f"DEVELOPMENT | {dev_mets[0]*100:.2f}% | {dev_mets[1]*100:.2f}% | {dev_mets[2]*100:.1f}%/{dev_mets[6]*100:.1f}% | {dev_mets[3]*100:.2f}%/{dev_mets[7]*100:.1f}% | {dev_mets[4]*100:.1f}%/{dev_mets[8]*100:.1f}% | {dev_mets[5]*100:.1f}%/{dev_mets[9]*100:.1f}%")

print("\n=== B2: SCORE DEFINITION FIX ===")
# Evaluate score at 0.5% and 5% prevalence
def eval_score_at_prev(df_split, rate, w_fn):
    dfs_res = []
    families = df_split['family'].unique()
    for fam in families:
        df_fam = df_split[df_split['family'] == fam]
        n_total = 2000
        n_def = int(n_total * rate)
        n_neg = n_total - n_def
        df_def = df_fam[df_fam['is_defective'] == 1]
        df_neg = df_fam[df_fam['is_defective'] == 0]
        df_def = df_def.sample(n=n_def, random_state=42)
        df_neg = df_neg.sample(n=n_neg, random_state=42)
        df_eval = pd.concat([df_def, df_neg]).reset_index(drop=True)
        dfs_res.append(evaluator.end_to_end_disposition(df_eval, module_a, module_b, k_noise=3.5))
    df_res = pd.concat(dfs_res)
    tp = len(df_res[(df_res['is_defective'] == 1) & (df_res['final_flag'] == 1)])
    fn = len(df_res[(df_res['is_defective'] == 1) & (df_res['final_flag'] == 0)])
    fp = len(df_res[(df_res['is_defective'] == 0) & (df_res['final_flag'] == 1)])
    n_total = len(df_res)
    
    score10 = evaluator.calculate_score(fp, fn, n_total, w_fn=10)
    score50 = evaluator.calculate_score(fp, fn, n_total, w_fn=50)
    score100 = evaluator.calculate_score(fp, fn, n_total, w_fn=100)
    return score10, score50, score100

s_05 = eval_score_at_prev(df_dev, 0.005, 50)
s_50 = eval_score_at_prev(df_dev, 0.05, 50)
print(f"Prevalence 0.5% | Sc10: {s_05[0]:.1f} | Sc50: {s_05[1]:.1f} | Sc100: {s_05[2]:.1f}")
print(f"Prevalence 5.0% | Sc10: {s_50[0]:.1f} | Sc50: {s_50[1]:.1f} | Sc100: {s_50[2]:.1f}")

# Detectability ceiling
print("\nDetectability Ceiling (24h divergerence > noise floor)")
all_mechs = list(df_dev['mechanism'].unique())
for mech in all_mechs:
    df_mech = df_dev[df_dev['mechanism'] == mech]
    # To find if they are detectable, we need baseline variation...
    # But wait, defect magnitude at 24h. We can just check the evaluated ones
    df_mech_eval = df_dev_eval[df_dev_eval['mechanism'] == mech]
    # Wait, the threshold is allowed_slope + slope_tolerance
    # Let's define detectable at 24h: measured_slope > allowed_slope + slope_tolerance
    detectable = df_mech_eval['measured_slope'] > (df_mech_eval['allowed_slope'] + df_mech_eval.get('slope_tolerance', 0))
    ceiling = detectable.mean()
    cond_recall = df_mech_eval[detectable]['final_flag'].mean() if ceiling > 0 else 0.0
    unc_recall = df_mech_eval['final_flag'].mean()
    print(f"Mech: {mech} | Ceiling: {ceiling*100:.1f}% | Cond Recall: {cond_recall*100:.1f}% | Uncond Recall: {unc_recall*100:.1f}%")

