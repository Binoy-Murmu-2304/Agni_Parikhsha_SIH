import json
import pandas as pd
from agnipariksha.config import FAMILY_SPECS
from agnipariksha.module_a.outlier import DynamicOutlierDetector
from agnipariksha.module_b.predictor import DriftPredictor
from agnipariksha.evaluation.evaluator import AgniEvaluator
from agnipariksha.qa_cards.generator import QACardGenerator
from agnipariksha.explainability.explainer import AgniExplainer

with open('data/manifest.json') as f:
    manifest = json.load(f)
df = pd.read_csv('data/dataset.csv')
train_lots = [x['lot_id'] for x in manifest['TRAIN']]
cal_lots = [x['lot_id'] for x in manifest['CALIBRATION']]
eval_lots = df[~df['lot_id'].isin(train_lots)]

mod_b = DriftPredictor()
df_train = df[df['lot_id'].isin(train_lots)]
df_cal = df[df['lot_id'].isin(cal_lots)]
mod_b.fit(df_train, df_cal)
mod_a = DynamicOutlierDetector()
evaluator = AgniEvaluator()
qa_gen = QACardGenerator()
explainer = AgniExplainer(mod_b)

res = []
for lot_id, lot_data in eval_lots.groupby('lot_id'):
    res.append(evaluator.end_to_end_disposition(lot_data, mod_a, mod_b, k_noise=3.5))
df_res = pd.concat(res)

routed_comp = df_res[(df_res['family'] == 'DIGITAL_IC') & (df_res['trigger_safety_slope'] == 1)].iloc[0]
auto_comp = df_res[(df_res['family'] == 'MEMS_GYROSCOPE') & (df_res['disposition'] == 'RED')].iloc[0]

def get_md(row):
    comp_df = df_res[df_res['component_id'] == row['component_id']].copy()
    exp = explainer.explain_instance(comp_df, row['family'])
    
    return qa_gen.generate_card(
        comp_id=row['component_id'],
        family=row['family'],
        verdict=row['disposition'],
        risk_tier='HIGH' if row['disposition'] == 'RED' else 'MEDIUM',
        measured_24h=row.get('value_24h', 0.0),
        pred_168h=row.get('pred_168h', 0.0),
        margin=(row.get('allowed_slope', 0.0) - row.get('measured_slope', 0.0)),
        conformal_90=row.get('conformal_radius_90', 0.0),
        explanation=exp,
        explainer=explainer,
        module_a_outlier=bool(row.get('trigger_module_a', 0)),
        safety_slope_breach=bool(row.get('trigger_safety_slope', 0)),
        capability_fallback=row.get('disposition') == 'FULL_BURN_IN'
    )

with open('routed_qa_card.md', 'w') as f:
    f.write(get_md(routed_comp))
with open('auto_qa_card.md', 'w') as f:
    f.write(get_md(auto_comp))

