import pandas as pd
import json
import numpy as np
from agnipariksha.module_a.outlier import DynamicOutlierDetector
from agnipariksha.module_b.predictor import DriftPredictor
from agnipariksha.evaluation.evaluator import AgniEvaluator
from agnipariksha.config import FAMILY_SPECS

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

# R1 Diagnosis on Healthy Blind Parts
df_blind_eval = evaluator.end_to_end_disposition(df_blind, module_a, module_b)
healthy_blind = df_blind_eval[df_blind_eval['is_defective'] == 0]

print("=== R1: TRIGGER ATTRIBUTION (Healthy Blind) ===")
print("Total Healthy Blind:", len(healthy_blind))
print("Module A RED:", healthy_blind['trigger_module_a'].mean() * 100, "%")
print("Safety Slope RED:", healthy_blind['trigger_safety_slope'].mean() * 100, "%")
print("Lot Stat Yellow:", healthy_blind['trigger_lot_stat'].mean() * 100, "%")
print("Conformal Breach RED:", healthy_blind['trigger_conformal'].mean() * 100, "%")
print("Final FPR:", healthy_blind['final_flag'].mean() * 100, "%")

