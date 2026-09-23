import pandas as pd
from agnipariksha.module_a.outlier import DynamicOutlierDetector
from agnipariksha.module_b.predictor import DriftPredictor
from agnipariksha.evaluation.evaluator import AgniEvaluator
import json

df_main = pd.read_csv("data/dataset.csv")
with open("data/manifest.json", "r") as f: manifest = json.load(f)
blind_lots = [item['lot_id'] for item in manifest['BLIND_TEST']]
df_blind = df_main[df_main['lot_id'].isin(blind_lots)]

module_b = DriftPredictor()
df_train = df_main[df_main['lot_id'].isin([item['lot_id'] for item in manifest['TRAIN']])]
df_cal = df_main[df_main['lot_id'].isin([item['lot_id'] for item in manifest['CALIBRATION']])]
module_b.fit(df_train, df_cal)

module_a = DynamicOutlierDetector()
evaluator = AgniEvaluator()

df_eval = evaluator.end_to_end_disposition(df_blind, module_a, module_b)
print("Module A Verdicts:", df_eval['module_a_verdict'].value_counts().to_dict())
print("Module B Verdicts:", df_eval['module_b_verdict'].value_counts().to_dict())
