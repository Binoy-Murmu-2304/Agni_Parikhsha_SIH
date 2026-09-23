import pandas as pd
import json
import numpy as np
from agnipariksha.evaluation.evaluator import AgniEvaluator
from agnipariksha.module_a.outlier import DynamicOutlierDetector
from agnipariksha.module_b.predictor import DriftPredictor

# 1. Load Data
df_main = pd.read_csv("data/dataset.csv")
with open("data/manifest.json", "r") as f: manifest = json.load(f)
df_train = df_main[df_main['lot_id'].isin([item['lot_id'] for item in manifest['TRAIN']])]
df_cal = df_main[df_main['lot_id'].isin([item['lot_id'] for item in manifest['CALIBRATION']])]
df_blind = df_main[df_main['lot_id'].isin([item['lot_id'] for item in manifest['BLIND_TEST']])]

module_b = DriftPredictor()
module_b.fit(df_train, df_cal)
module_a = DynamicOutlierDetector()
evaluator = AgniEvaluator()

df_b = []
for lot_id, lot_data in df_blind.groupby("lot_id"):
    df_b.append(evaluator.end_to_end_disposition(lot_data, module_a, module_b, k_noise=3.5))
df_blind_eval = pd.concat(df_b)
healthy_blind = df_blind_eval[df_blind_eval['is_defective'] == 0]

print("Module A RED:", healthy_blind['trigger_module_a'].mean() * 100, "%")
print("Safety Slope RED:", healthy_blind['trigger_safety_slope'].mean() * 100, "%")
print("Lot Stat Yellow:", healthy_blind['trigger_lot_stat'].mean() * 100, "%")
print("Conformal Breach RED:", healthy_blind['trigger_conformal'].mean() * 100, "%")
print("Final FPR:", healthy_blind['final_flag'].mean() * 100, "%")
