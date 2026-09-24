import json
import os
import io
import math
import tempfile
import zipfile
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from agnipariksha.config import FAMILY_SPECS, CAPABILITY_ROUTING
from agnipariksha.module_a.outlier import DynamicOutlierDetector
from agnipariksha.module_b.predictor import DriftPredictor
from agnipariksha.evaluation.evaluator import AgniEvaluator
from agnipariksha.qa_cards.generator import QACardGenerator
from agnipariksha.qa_cards.pdf_export import generate_pdf_certificate
from agnipariksha.qa_cards.pdf_report import generate_pdf_lot_report

mod_a = None
mod_b = None
evaluator = None
qa_gen = None
df_cache = None

def derive_risk_tier(record: dict) -> str:
    raw_tier = record.get('risk_tier')
    if raw_tier is not None and not pd.isna(raw_tier):
        tier_str = str(raw_tier).upper()
        if tier_str in ('HIGH', 'MEDIUM', 'LOW'):
            return tier_str
    
    disp = str(record.get('disposition', '')).upper()
    if disp == 'RED':
        return 'HIGH'
    elif disp == 'FULL_BURN_IN':
        return 'MEDIUM'
    else:
        return 'LOW'

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
    df_cache['risk_tier'] = df_cache['disposition'].apply(lambda d: 'HIGH' if d == 'RED' else 'MEDIUM' if d == 'FULL_BURN_IN' else 'LOW')
    yield

app = FastAPI(title="AGNI PARIKSHA API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/lots")
def list_lots():
    if df_cache is None or len(df_cache) == 0:
        return []
    
    out = []
    for lot_id, df_lot in df_cache.groupby('lot_id', sort=False):
        family = str(df_lot['family'].iloc[0]) if 'family' in df_lot.columns else "UNKNOWN"
        total = len(df_lot)
        counts = df_lot['disposition'].value_counts().to_dict()
        green = counts.get('GREEN', 0)
        full_burn_in = counts.get('FULL_BURN_IN', 0)
        red = counts.get('RED', 0)
        
        defects_detected = red
        if 'is_defective' in df_lot.columns:
            defects_in_lot = int(df_lot['is_defective'].sum())
        else:
            defects_in_lot = red + full_burn_in
            
        out.append({
            "lot_id": lot_id,
            "family": family,
            "total": total,
            "green": green,
            "full_burn_in": full_burn_in,
            "red": red,
            "defects_detected": defects_detected,
            "defects_in_lot": defects_in_lot
        })
    return out

@app.get("/components/all")
def get_all_components(disposition: str = None, family: str = None, search: str = None, page: int = 1, per_page: int = 50):
    if df_cache is None or len(df_cache) == 0:
        return {"total": 0, "counts": {"GREEN": 0, "FULL_BURN_IN": 0, "RED": 0}, "page": page, "per_page": per_page, "components": []}
    
    df_filtered = df_cache
    if family and family != 'ALL':
        df_filtered = df_filtered[df_filtered['family'] == family]
    if search:
        search_lower = search.lower()
        df_filtered = df_filtered[
            df_filtered['component_id'].astype(str).str.lower().str.contains(search_lower) |
            df_filtered['lot_id'].astype(str).str.lower().str.contains(search_lower)
        ]
        
    counts = df_filtered['disposition'].value_counts().to_dict()
    counts_dict = {
        "GREEN": int(counts.get('GREEN', 0)),
        "FULL_BURN_IN": int(counts.get('FULL_BURN_IN', 0)),
        "RED": int(counts.get('RED', 0))
    }
    
    df_disp = df_filtered
    if disposition:
        df_disp = df_disp[df_disp['disposition'] == disposition]
        
    disp_order = {'RED': 0, 'FULL_BURN_IN': 1, 'GREEN': 2}
    df_disp = df_disp.copy()
    df_disp['sort_key'] = df_disp['disposition'].map(lambda d: disp_order.get(d, 3))
    df_disp = df_disp.sort_values(by=['sort_key', 'lot_id', 'component_id'])
    
    total_count = len(df_disp)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    df_page = df_disp.iloc[start_idx:end_idx]
    
    components = []
    for record in df_page.to_dict(orient="records"):
        fam = str(record.get('family', 'DIGITAL_IC'))
        spec_info = FAMILY_SPECS.get(fam, {})
        margin = (record.get('allowed_slope', 0.0) - record.get('measured_slope', 0.0)) if not pd.isna(record.get('allowed_slope')) and not pd.isna(record.get('measured_slope')) else None
        
        comp_dict = {
            "component_id": str(record['component_id']),
            "lot_id": str(record['lot_id']),
            "family": fam,
            "disposition": str(record['disposition']),
            "risk_tier": derive_risk_tier(record),
            "pred_168h": record.get('pred_168h') if not pd.isna(record.get('pred_168h')) else None,
            "measured_slope": record.get('measured_slope') if not pd.isna(record.get('measured_slope')) else None,
            "allowed_slope": record.get('allowed_slope') if not pd.isna(record.get('allowed_slope')) else None,
            "safety_slope_margin": margin,
            "trigger_module_a": int(record.get('trigger_module_a', 0)),
            "trigger_safety_slope": int(record.get('trigger_safety_slope', 0)),
            "conformal_interval_95": record.get('conformal_radius_95') if not pd.isna(record.get('conformal_radius_95')) else None,
            "spec_max": spec_info.get('spec_max', 50.0),
            "unit": spec_info.get('unit', 'µA'),
            "value_0h": record.get('value_0h') if not pd.isna(record.get('value_0h')) else None,
            "value_24h": record.get('value_24h') if not pd.isna(record.get('value_24h')) else None,
        }
        components.append(comp_dict)
        
    return {
        "total": total_count,
        "counts": counts_dict,
        "page": page,
        "per_page": per_page,
        "components": components
    }

@app.get("/lots/{lot_id}/components")
def get_lot_components(lot_id: str, disposition: str = None, page: int = 1, per_page: int = 50):
    df_lot = df_cache[df_cache['lot_id'] == lot_id]
    if len(df_lot) == 0:
        raise HTTPException(404, "Lot not found")
        
    if disposition:
        df_lot = df_lot[df_lot['disposition'] == disposition]
        
    disp_order = {'RED': 0, 'FULL_BURN_IN': 1, 'GREEN': 2}
    df_lot = df_lot.copy()
    df_lot['sort_key'] = df_lot['disposition'].map(lambda d: disp_order.get(d, 3))
    df_lot = df_lot.sort_values(by=['sort_key', 'component_id'])
    
    total_count = len(df_lot)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    df_page = df_lot.iloc[start_idx:end_idx]
    
    components = []
    for record in df_page.to_dict(orient="records"):
        fam = str(record.get('family', 'DIGITAL_IC'))
        spec_info = FAMILY_SPECS.get(fam, {})
        margin = (record.get('allowed_slope', 0.0) - record.get('measured_slope', 0.0)) if not pd.isna(record.get('allowed_slope')) and not pd.isna(record.get('measured_slope')) else None
        
        comp_dict = {
            "component_id": str(record['component_id']),
            "lot_id": str(record['lot_id']),
            "family": fam,
            "disposition": str(record['disposition']),
            "risk_tier": derive_risk_tier(record),
            "pred_168h": record.get('pred_168h') if not pd.isna(record.get('pred_168h')) else None,
            "measured_slope": record.get('measured_slope') if not pd.isna(record.get('measured_slope')) else None,
            "allowed_slope": record.get('allowed_slope') if not pd.isna(record.get('allowed_slope')) else None,
            "safety_slope_margin": margin,
            "trigger_module_a": int(record.get('trigger_module_a', 0)),
            "trigger_safety_slope": int(record.get('trigger_safety_slope', 0)),
            "conformal_interval_95": record.get('conformal_radius_95') if not pd.isna(record.get('conformal_radius_95')) else None,
            "spec_max": spec_info.get('spec_max', 50.0),
            "unit": spec_info.get('unit', 'µA'),
            "value_0h": record.get('value_0h') if not pd.isna(record.get('value_0h')) else None,
            "value_24h": record.get('value_24h') if not pd.isna(record.get('value_24h')) else None,
        }
        components.append(comp_dict)
        
    return {
        "lot_id": lot_id,
        "total": total_count,
        "page": page,
        "per_page": per_page,
        "components": components
    }

@app.post("/lots/screen")
def screen_lot(records: list[dict]):
    df = pd.DataFrame(records)
    if 'value_24h' not in df.columns:
        raise HTTPException(400, "value_24h is required")
    res = []
    for lot_id, lot_data in df.groupby('lot_id'):
        res.append(evaluator.end_to_end_disposition(lot_data, mod_a, mod_b, k_noise=3.5))
    df_res = pd.concat(res)
    
    df_res['risk_tier'] = df_res['disposition'].apply(lambda d: 'HIGH' if d == 'RED' else 'MEDIUM' if d == 'FULL_BURN_IN' else 'LOW')
    global df_cache
    df_cache = pd.concat([df_cache, df_res]).drop_duplicates(subset=['component_id'], keep='last')
    
    out = []
    for record in df_res.to_dict(orient="records"):
        out_rec = {}
        for k, v in record.items():
            if isinstance(v, float) and math.isnan(v):
                out_rec[k] = None
            else:
                out_rec[k] = v
        out_rec['risk_tier'] = derive_risk_tier(record)
        out.append(out_rec)
    return out

@app.get("/components/{id}")
def get_component(id: str):
    df_c = df_cache[df_cache['component_id'] == id]
    if len(df_c) == 0:
        raise HTTPException(404, "Component not found")
    row = df_c.iloc[0]
    fam = str(row.get('family', 'DIGITAL_IC'))
    spec_info = FAMILY_SPECS.get(fam, {})
    
    return {
        "component_id": str(row['component_id']),
        "lot_id": str(row.get('lot_id', 'LOT_0001')),
        "family": fam,
        "disposition": str(row['disposition']),
        "risk_tier": derive_risk_tier(row.to_dict()),
        "pred_168h": row.get('pred_168h') if not pd.isna(row.get('pred_168h')) else None,
        "conformal_interval_95": row.get('conformal_radius_95') if not pd.isna(row.get('conformal_radius_95')) else None,
        "safety_slope_margin": (row.get('allowed_slope') - row.get('measured_slope')) if not pd.isna(row.get('allowed_slope')) and not pd.isna(row.get('measured_slope')) else None,
        "measured_slope": row.get('measured_slope') if not pd.isna(row.get('measured_slope')) else None,
        "allowed_slope": row.get('allowed_slope') if not pd.isna(row.get('allowed_slope')) else None,
        "trigger_module_a": int(row.get('trigger_module_a', 0)),
        "trigger_safety_slope": int(row.get('trigger_safety_slope', 0)),
        "value_0h": row.get('value_0h') if not pd.isna(row.get('value_0h')) else None,
        "value_24h": row.get('value_24h') if not pd.isna(row.get('value_24h')) else None,
        "spec_max": spec_info.get('spec_max', 50.0),
        "unit": spec_info.get('unit', 'µA')
    }

@app.get("/components/{id}/card")
def get_component_card(id: str):
    df_c = df_cache[df_cache['component_id'] == id]
    if len(df_c) == 0:
        raise HTTPException(404, "Component not found")
    row = df_c.iloc[0]
    
    margin_val = (row.get('allowed_slope', 0.0) - row.get('measured_slope', 0.0)) if not pd.isna(row.get('allowed_slope')) and not pd.isna(row.get('measured_slope')) else 0.0
    conformal_val = row.get('conformal_radius_90', 0.0) if not pd.isna(row.get('conformal_radius_90')) else 0.0
    measured_val = row.get('value_24h', 0.0) if not pd.isna(row.get('value_24h')) else 0.0
    pred_val = row.get('pred_168h', 0.0) if not pd.isna(row.get('pred_168h')) else 0.0

    md = qa_gen.generate_card(
        comp_id=str(row['component_id']),
        family=str(row.get('family', 'DIGITAL_IC')),
        verdict=str(row.get('disposition', 'GREEN')),
        risk_tier=str(row.get('risk_tier', 'LOW')),
        measured_24h=float(measured_val),
        pred_168h=float(pred_val),
        margin=float(margin_val),
        conformal_90=float(conformal_val),
        explanation={'top_features': [], 'base_value': 0.0},
        explainer=None
    )
    return {"markdown": md}

@app.get("/components/{id}/certificate")
def get_component_certificate(id: str):
    df_c = df_cache[df_cache['component_id'] == id]
    if len(df_c) == 0:
        raise HTTPException(404, "Component not found")
    row = df_c.iloc[0]
    
    fam = str(row.get('family', 'DIGITAL_IC'))
    spec_info = FAMILY_SPECS.get(fam, {})
    unit = spec_info.get('unit', '')
    
    margin_val = (row.get('allowed_slope', 0.0) - row.get('measured_slope', 0.0)) if not pd.isna(row.get('allowed_slope')) and not pd.isna(row.get('measured_slope')) else None
    margin_str = f"{margin_val:+.4f}" if margin_val is not None else "not computed"
    
    conf_val = row.get('conformal_radius_95') if not pd.isna(row.get('conformal_radius_95')) else None
    conf_str = f"± {conf_val:.2f} {unit}" if conf_val is not None else "not computed"
    
    pred_val = row.get('pred_168h') if not pd.isna(row.get('pred_168h')) else None
    pred_str = f"{pred_val:.2f} {unit}" if pred_val is not None else "not computed"
    
    disp = str(row.get('disposition', 'GREEN'))
    reasons = []
    if int(row.get('trigger_module_a', 0)):
        reasons.append("Module A dynamic outlier detected")
    if int(row.get('trigger_safety_slope', 0)):
        reasons.append("Safety slope breach detected")
    if disp == "FULL_BURN_IN" and not reasons:
        reasons.append("Capability audit policy routing override")
    if not reasons:
        reasons.append("Nominal parameter trajectory")

    card_data = {
        "component_id": str(row['component_id']),
        "lot_id": str(row.get('lot_id', 'LOT_0001')),
        "family": fam,
        "disposition": disp,
        "risk_tier": str(row.get('risk_tier', 'LOW')),
        "reasons": reasons,
        "pred_168h": pred_str,
        "margin": margin_str,
        "interval": conf_str,
        "routing_rationale": "Mandatory 168h burn-in per family capability policy" if disp == "FULL_BURN_IN" else "24h early exit certified" if disp == "GREEN" else "Rejected due to drift bounds breach"
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp_path = tmp.name
        
    generate_pdf_certificate(card_data, tmp_path)
    
    with open(tmp_path, "rb") as f:
        pdf_bytes = f.read()
        
    os.unlink(tmp_path)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="AGNI_PARIKSHA_{id}_certificate.pdf"'
        }
    )

@app.get("/lots/{lot_id}/certificates")
def get_lot_certificates_zip(lot_id: str):
    df_lot = df_cache[df_cache['lot_id'] == lot_id]
    if len(df_lot) == 0:
        raise HTTPException(404, "Lot not found")
        
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        flagged = df_lot[df_lot['disposition'].isin(['RED', 'FULL_BURN_IN'])].head(50)
        for _, row in flagged.iterrows():
            cid = str(row['component_id'])
            fam = str(row.get('family', 'DIGITAL_IC'))
            spec_info = FAMILY_SPECS.get(fam, {})
            unit = spec_info.get('unit', '')
            
            margin_val = (row.get('allowed_slope', 0.0) - row.get('measured_slope', 0.0)) if not pd.isna(row.get('allowed_slope')) and not pd.isna(row.get('measured_slope')) else None
            margin_str = f"{margin_val:+.4f}" if margin_val is not None else "not computed"
            
            conf_val = row.get('conformal_radius_95') if not pd.isna(row.get('conformal_radius_95')) else None
            conf_str = f"± {conf_val:.2f} {unit}" if conf_val is not None else "not computed"
            
            pred_val = row.get('pred_168h') if not pd.isna(row.get('pred_168h')) else None
            pred_str = f"{pred_val:.2f} {unit}" if pred_val is not None else "not computed"
            disp = str(row.get('disposition', 'GREEN'))

            reasons = []
            if int(row.get('trigger_module_a', 0)): reasons.append("Module A outlier")
            if int(row.get('trigger_safety_slope', 0)): reasons.append("Safety slope breach")
            if disp == "FULL_BURN_IN" and not reasons: reasons.append("Capability audit routing override")
            if not reasons: reasons.append("Nominal trajectory")

            card_data = {
                "component_id": cid,
                "lot_id": lot_id,
                "family": fam,
                "disposition": disp,
                "risk_tier": str(row.get('risk_tier', 'MEDIUM')),
                "reasons": reasons,
                "pred_168h": pred_str,
                "margin": margin_str,
                "interval": conf_str,
                "routing_rationale": "Mandatory full burn-in routing" if disp == "FULL_BURN_IN" else "Reject"
            }
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp_path = tmp.name
            generate_pdf_certificate(card_data, tmp_path)
            with open(tmp_path, "rb") as pf:
                pdf_bytes = pf.read()
            os.unlink(tmp_path)
            zf.writestr(f"AGNI_PARIKSHA_{cid}_certificate.pdf", pdf_bytes)

        green_parts = df_lot[df_lot['disposition'] == 'GREEN']
        if len(green_parts) > 0:
            summary_card = {
                "component_id": f"{lot_id}_GREEN_SUMMARY",
                "lot_id": lot_id,
                "family": str(df_lot['family'].iloc[0]),
                "disposition": "GREEN_EARLY_EXIT_PASSED",
                "risk_tier": "LOW",
                "reasons": [f"{len(green_parts)} components certified for 24h early exit"],
                "pred_168h": "ALL_IN_SPEC",
                "margin": "POSITIVE",
                "interval": "NOMINAL",
                "routing_rationale": "Certified 24h Early Exit"
            }
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp_path = tmp.name
            generate_pdf_certificate(summary_card, tmp_path)
            with open(tmp_path, "rb") as pf:
                pdf_bytes = pf.read()
            os.unlink(tmp_path)
            zf.writestr(f"AGNI_PARIKSHA_{lot_id}_PASS_summary.pdf", pdf_bytes)

    zip_bytes = zip_buffer.getvalue()
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="AGNI_PARIKSHA_{lot_id}_certificates.zip"'
        }
    )

@app.get("/lots/{lot_id}/report")
def get_lot_report(lot_id: str):
    is_fleet = (lot_id.lower() in ["all", "fleet"])
    if not is_fleet and (df_cache is None or len(df_cache[df_cache['lot_id'] == lot_id]) == 0):
        raise HTTPException(404, f"Lot {lot_id} not found")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp_path = tmp.name

    with open("metrics_canonical.json", "r") as mf:
        metrics_data = json.load(mf)

    generate_pdf_lot_report(lot_id, df_cache, metrics_data, tmp_path, report_date="2026-09-24")

    with open(tmp_path, "rb") as f:
        pdf_bytes = f.read()

    os.unlink(tmp_path)

    filename = "AGNI_PARIKSHA_FLEET_REPORT_2026-09-24.pdf" if is_fleet else f"AGNI_PARIKSHA_LOT_REPORT_{lot_id}_2026-09-24.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

@app.get("/lots/{id}/summary")
def get_lot_summary(id: str):
    df_lot = df_cache[df_cache['lot_id'] == id]
    if len(df_lot) == 0:
        raise HTTPException(404, "Lot not found")
    
    counts = df_lot['disposition'].value_counts().to_dict()
    green_count = counts.get('GREEN', 0)
    total_count = len(df_lot)
    green_fraction = green_count / total_count if total_count > 0 else 0.0

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
        "total": total_count,
        "green_count": green_count,
        "green_fraction": round(green_fraction, 4),
        "realized_savings": round(realized_savings, 2),
        "yield_assumption": f"Based on evaluated lot defect rate ({round(green_fraction * 100, 1)}% GREEN yield)"
    }

@app.get("/metrics")
def get_metrics():
    with open("metrics_canonical.json", "r") as f:
        return json.load(f)
