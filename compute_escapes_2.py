import pandas as pd
import json
import scipy.stats

with open('data/manifest.json', 'r') as f:
    manifest = json.load(f)

df = pd.read_csv('data/dataset.csv')
final_lots = [x['lot_id'] for x in manifest['FINAL_EVAL']]
df_final = df[df['lot_id'].isin(final_lots)]

# Escapes are defects that are NOT FINAL_FLAG=1 and are NOT in a ROUTED family
# Wait, let's just compute it from the evaluator outputs!
from agnipariksha.config import CAPABILITY_ROUTING
from agnipariksha.module_a.outlier import DynamicOutlierDetector
from agnipariksha.module_b.predictor import DriftPredictor
from agnipariksha.evaluation.evaluator import AgniEvaluator

train_lots = [item['lot_id'] for item in manifest['TRAIN']]
cal_lots = [item['lot_id'] for item in manifest['CALIBRATION']]
df_train = df[df['lot_id'].isin(train_lots)]
df_cal = df[df['lot_id'].isin(cal_lots)]

mod_b = DriftPredictor()
mod_b.fit(df_train, df_cal)
mod_a = DynamicOutlierDetector()
evaluator = AgniEvaluator()

res = []
for lot_id, lot_data in df_final.groupby('lot_id'):
    # We must inject 5% defects to see the 98 escapes!
    # Wait, the 98 escapes are from the 5% prevalence run.
    pass

