import pandas as pd
from agnipariksha.module_b.predictor import DriftPredictor
from agnipariksha.explainability.explainer import AgniExplainer
from agnipariksha.qa_cards.generator import QACardGenerator
import json
df_main = pd.read_csv("data/dataset.csv")
with open("data/manifest.json", "r") as f: manifest = json.load(f)
df_train = df_main[df_main['lot_id'].isin([item['lot_id'] for item in manifest['TRAIN']])]
df_cal = df_main[df_main['lot_id'].isin([item['lot_id'] for item in manifest['CALIBRATION']])]
module_b = DriftPredictor()
module_b.fit(df_train, df_cal)
explainer = AgniExplainer(module_b)
gen = QACardGenerator('qa_cards_output')

# RED card
df_blind = df_main[df_main['lot_id'].isin([item['lot_id'] for item in manifest['BLIND_TEST']])]
df_b = module_b.compute_safety_slope(df_blind, current_hour=24)
red_row = df_b[df_b['module_b_verdict'] == 'RED_SAFETY_SLOPE'].iloc[0]
df_red = df_blind.loc[[red_row.name]]
explanation = explainer.explain_instance(df_red, red_row['family'])
margin = red_row['allowed_slope'] + red_row['slope_tolerance'] - max(red_row['measured_slope'], red_row['pred_slope'])
gen.generate_card('REGEN_COMP_RED', red_row['family'], red_row['module_b_verdict'], red_row['module_b_verdict'], red_row['value_24h'], red_row['pred_168h'], margin, module_b.q_alphas_90.get(red_row['family'], 0.0), explanation, explainer)

# GREEN card
green_row = df_b[df_b['module_b_verdict'] == 'GREEN'].iloc[0]
df_green = df_blind.loc[[green_row.name]]
explanation = explainer.explain_instance(df_green, green_row['family'])
margin = green_row['allowed_slope'] + green_row['slope_tolerance'] - max(green_row['measured_slope'], green_row['pred_slope'])
gen.generate_card('REGEN_COMP_GREEN', green_row['family'], green_row['module_b_verdict'], green_row['module_b_verdict'], green_row['value_24h'], green_row['pred_168h'], margin, module_b.q_alphas_90.get(green_row['family'], 0.0), explanation, explainer)
