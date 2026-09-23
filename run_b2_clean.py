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
df_train = df_main[df_main['lot_id'].isin(train_lots)]
df_cal = df_main[df_main['lot_id'].isin(cal_lots)]
df_dev = df_main[df_main['lot_id'].isin(dev_lots)]

module_b = DriftPredictor()
module_b.fit(df_train, df_cal)
module_a = DynamicOutlierDetector()
evaluator = AgniEvaluator()

df_prev = evaluator.evaluate_prevalence(df_dev, module_a, module_b, prevalence_rates=[0.005, 0.05], k_noise=3.5)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
print(df_prev)
