import pandas as pd
import json
import numpy as np
from agnipariksha.module_a.outlier import DynamicOutlierDetector
from agnipariksha.module_b.predictor import DriftPredictor
from agnipariksha.evaluation.evaluator import AgniEvaluator

# 1. Load Data
df_main = pd.read_csv("data/dataset.csv")
with open("data/manifest.json", "r") as f: manifest = json.load(f)
df_train = df_main[df_main['lot_id'].isin([item['lot_id'] for item in manifest['TRAIN']])]
df_cal = df_main[df_main['lot_id'].isin([item['lot_id'] for item in manifest['CALIBRATION']])]
df_blind = df_main[df_main['lot_id'].isin([item['lot_id'] for item in manifest['BLIND_TEST']])]

# Fit Model
module_b = DriftPredictor()
module_b.fit(df_train, df_cal)
module_a = DynamicOutlierDetector()
evaluator = AgniEvaluator()

print("=== R2: THRESHOLD SWEEP ON CALIBRATION ===")
best_k = 3.5
min_fpr = 1.0

# Pre-evaluate module A & predictions
# We can just run end_to_end once with k=0 and then modify df_b['trigger_safety_slope']
df_cal_eval = evaluator.end_to_end_disposition(df_cal, module_a, module_b, k_noise=0.0)

for k_noise in [3.0, 3.5, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0]:
    # Evaluate safety slope flag logic
    df = df_cal_eval.copy()
    df['trigger_safety_slope'] = (df[['measured_slope', 'pred_slope']].max(axis=1) > (df['allowed_slope'] + k_noise * (1.4826 * df['lot_stat_bound'] / 3.5))).astype(int)
    # wait, lot_stat_bound is median + K * mad. I don't have mad_slope in the df.
    # Let's just run end_to_end_disposition properly
    
    dfs_res = []
    for lot_id, lot_data in df_cal.groupby('lot_id'):
        dfs_res.append(evaluator.end_to_end_disposition(lot_data, module_a, module_b, k_noise=k_noise))
    df_res = pd.concat(dfs_res)
    
    healthy = df_res[df_res['is_defective'] == 0]
    defect = df_res[df_res['is_defective'] == 1]
    
    fpr = healthy['final_flag'].mean()
    recall = defect['final_flag'].mean()
    
    tp = defect['final_flag'].sum()
    fp = healthy['final_flag'].sum()
    precision = tp / max(1, tp + fp)
    fw_per_1000 = fp / len(healthy) * 1000
    
    # FN-weighted score (let's assume total N = len(df_res))
    fn = len(defect) - tp
    score_10 = evaluator.calculate_score(fp, fn, len(df_res), w_fn=10)
    score_50 = evaluator.calculate_score(fp, fn, len(df_res), w_fn=50)
    score_100 = evaluator.calculate_score(fp, fn, len(df_res), w_fn=100)
    
    print(f"k_noise={k_noise:4.1f} | FPR: {fpr*100:5.2f}% | Recall: {recall*100:5.2f}% | Prec: {precision*100:5.2f}% | FW/1000: {fw_per_1000:5.1f} | Sc10: {score_10:5.1f} | Sc50: {score_50:5.1f} | Sc100: {score_100:5.1f}")
    if fpr <= 0.05 and k_noise < best_k if min_fpr > 0.05 else True: # simplistic, let's just pick visually later
        pass

