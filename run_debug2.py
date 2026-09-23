import pandas as pd
from agnipariksha.evaluation.evaluator import AgniEvaluator
from agnipariksha.module_a.outlier import DynamicOutlierDetector
from agnipariksha.module_b.predictor import DriftPredictor
import json

df = pd.read_csv('data/dataset.csv')
with open('data/manifest.json') as f:
    m = json.load(f)
train = [x['lot_id'] for x in m['TRAIN']]
cal = [x['lot_id'] for x in m['CALIBRATION']]
dev = [x['lot_id'] for x in m['DEVELOPMENT']]

df_train = df[df['lot_id'].isin(train)]
df_cal = df[df['lot_id'].isin(cal)]
df_dev = df[df['lot_id'].isin(dev)]

mod_b = DriftPredictor()
mod_b.fit(df_train, df_cal)
mod_a = DynamicOutlierDetector()
ev = AgniEvaluator()

df_res = ev.end_to_end_disposition(df_dev[df_dev['family']=='DIGITAL_IC'], mod_a, mod_b, 3.5)
green = df_res[df_res['disposition'] == 'FULL_BURN_IN']
print(green.iloc[0].to_dict())
