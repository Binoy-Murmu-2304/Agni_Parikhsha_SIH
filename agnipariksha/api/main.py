import json
import pandas as pd
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from agnipariksha.config import FAMILY_SPECS, CAPABILITY_ROUTING
from agnipariksha.module_a.outlier import DynamicOutlierDetector
from agnipariksha.module_b.predictor import DriftPredictor
from agnipariksha.evaluation.evaluator import AgniEvaluator
from agnipariksha.qa_cards.generator import QACardGenerator

mod_a = None
mod_b = None
evaluator = None
qa_gen = None
df_cache = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mod_a, mod_b, evaluator, qa_gen, df_cache
    df_main = pd.read_csv("data/dataset.csv")
    with open("data/manifest.json", "r") as f:
        manifest = json.load(f)
    train_lots = [item['lot_id'] for item in manifest['TRAIN']]
    cal_lots = [item['lot_id'] for item in manifest['CALIBRATION']]
    
    df_train = df_main[df_main['lot_id'].isin(train_lots)]
    df_cal = df_main[df_main['lot_id'].isin(cal_lots)]
    
    mod_b = DriftPredictor()
    mod_b.fit(df_train, df_cal)
    mod_a = DynamicOutlierDetector()
    evaluator = AgniEvaluator()
    qa_gen = QACardGenerator()
    
    # Pre-evaluate all lots (except train) to serve the dashboard instantly
    eval_lots = df_main[~df_main['lot_id'].isin(train_lots)]
    res = []
    for lot_id, lot_data in eval_lots.groupby('lot_id'):
        res.append(evaluator.end_to_end_disposition(lot_data, mod_a, mod_b, k_noise=3.5))
    df_cache = pd.concat(res)
    yield

app = FastAPI(title="AGNI PARIKSHA API", lifespan=lifespan)

@app.post("/lots/screen")
def screen_lot(records: list[dict]):
    df = pd.DataFrame(records)
    if 'value_24h' not in df.columns:
        raise HTTPException(400, "value_24h is required")
    res = []
    for lot_id, lot_data in df.groupby('lot_id'):
        res.append(evaluator.end_to_end_disposition(lot_data, mod_a, mod_b, k_noise=3.5))
    df_res = pd.concat(res)
    
    
    def map_risk(d):
        if d == 'RED': return 'HIGH'
        if d == 'FULL_BURN_IN': return 'MEDIUM'
        return 'LOW'
        
    df_res['risk_tier'] = df_res['disposition'].apply(map_risk)
    import math
    out = []
    for record in df_res.to_dict(orient="records"):
        out_rec = {}
        for k, v in record.items():
            if isinstance(v, float) and math.isnan(v):
                out_rec[k] = None
            else:
                out_rec[k] = v
        out.append(out_rec)
    return out

@app.get("/components/{id}")
def get_component(id: str):
    df_c = df_cache[df_cache['component_id'] == id]
    if len(df_c) == 0:
        raise HTTPException(404, "Component not found")
    row = df_c.iloc[0]
    return {
        "component_id": row['component_id'],
        "disposition": row['disposition'],
        "pred_168h": row.get('pred_168h') if not pd.isna(row.get('pred_168h')) else None,
        "conformal_interval_95": row.get('conformal_radius_95') if not pd.isna(row.get('conformal_radius_95')) else None,
        "safety_slope_margin": (row.get('allowed_slope') - row.get('measured_slope')) if not pd.isna(row.get('allowed_slope')) and not pd.isna(row.get('measured_slope')) else None,
        "measured_slope": row.get('measured_slope') if not pd.isna(row.get('measured_slope')) else None,
        "allowed_slope": row.get('allowed_slope') if not pd.isna(row.get('allowed_slope')) else None,
        "trigger_module_a": int(row.get('trigger_module_a', 0)),
        "trigger_safety_slope": int(row.get('trigger_safety_slope', 0)),
    }

@app.get("/components/{id}/card")
def get_component_card(id: str):
    df_c = df_cache[df_cache['component_id'] == id]
    if len(df_c) == 0:
        raise HTTPException(404, "Component not found")
    row = df_c.iloc[0]
    
    # We mock explanation/explainer since they are not in the df cache
    md = qa_gen.generate_card(
        comp_id=row['component_id'],
        family=row['family'],
        verdict=row['disposition'],
        risk_tier=row.get('risk_tier', 'HIGH'),
        measured_24h=row.get('value_24h', 0.0),
        pred_168h=row.get('pred_168h', 0.0),
        margin=(row.get('allowed_slope', 0.0) - row.get('measured_slope', 0.0)),
        conformal_90=row.get('conformal_radius_90', 0.0),
        explanation={'feature_importance': {}, 'base_value': 0.0},
        explainer=None
    )
    return {"markdown": md}

@app.get("/lots/{id}/summary")
def get_lot_summary(id: str):
    df_lot = df_cache[df_cache['lot_id'] == id]
    if len(df_lot) == 0:
        raise HTTPException(404, "Lot not found")
    
    counts = df_lot['disposition'].value_counts().to_dict()
    # Realized savings calculation (formula: sum share_f * exit_rate_f * 85.71%)
    with open('metrics_canonical.json', 'r') as mf:
        canonical = json.load(mf)
    failed = [fam for fam in FAMILY_SPECS.keys() if canonical.get(fam, {}).get('MAE', 0) / FAMILY_SPECS[fam]['spec_max'] > 0.20]
    
    realized_savings = 0.0
    share_f = 1 / len(FAMILY_SPECS)
    for fam in FAMILY_SPECS.keys():
        if fam in failed:
            exit_rate = 0.0
        else:
            df_fam = df_lot[df_lot['family'] == fam]
            if len(df_fam) == 0:
                continue
            exit_rate = len(df_fam[df_fam['disposition'] == 'GREEN']) / len(df_fam)
        realized_savings += share_f * exit_rate * 85.71
        
    return {
        "lot_id": id,
        "counts": counts,
        "realized_savings": round(realized_savings, 2),
        "yield_assumption": "Based on evaluated lot defect rate"
    }

@app.get("/metrics")
def get_metrics():
    with open("metrics_canonical.json", "r") as f:
        return json.load(f)
