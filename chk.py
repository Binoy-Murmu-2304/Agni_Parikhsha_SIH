import json
import pandas as pd
from agnipariksha.module_b.predictor import DriftPredictor
with open('data/manifest.json') as f:
    manifest = json.load(f)
df = pd.read_csv('data/dataset.csv')
train_lots = [x['lot_id'] for x in manifest['TRAIN']]
cal_lots = [x['lot_id'] for x in manifest['CALIBRATION']]
mod_b = DriftPredictor()
mod_b.fit(df[df['lot_id'].isin(train_lots)], df[df['lot_id'].isin(cal_lots)])
print(mod_b.q_alphas_90)
