import pandas as pd
from agnipariksha.module_b.predictor import DriftPredictor
import json

df_main = pd.read_csv("data/dataset.csv")
with open("data/manifest.json", "r") as f: manifest = json.load(f)
df_train = df_main[df_main['lot_id'].isin([item['lot_id'] for item in manifest['TRAIN']])]
df_cal = df_main[df_main['lot_id'].isin([item['lot_id'] for item in manifest['CALIBRATION']])]

module_b = DriftPredictor()
module_b.fit(df_train, df_cal)

df_blind = df_main[df_main['lot_id'].isin([item['lot_id'] for item in manifest['BLIND_TEST']])]
df_b = module_b.compute_safety_slope(df_blind, current_hour=24)

fail_df = df_b[df_b['module_b_verdict'] == 'RED_SAFETY_SLOPE'].head(2)
for i, row in fail_df.iterrows():
    print("Family:", row['family'])
    print("v0:", row['value_0h'], "v24:", row['value_24h'], "pred168:", row['pred_168h'])
    print("measured_slope:", row['measured_slope'], "pred_slope:", row['pred_slope'])
    print("allowed_slope:", row['allowed_slope'], "headroom:", row['headroom_bound'], "relative:", row['relative_bound'])
    print("---")
