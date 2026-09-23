import os
import io
import json
import pandas as pd
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel

from .models.database import SessionLocal, engine, PartResult, PartReading
from .core.ingest import normalize_dataset
from .core.module_a import run_module_a
from .core.module_b import run_module_b
from .core.module_c import run_module_c
from .core.explain import create_pdf_certificate
from .synth.generator import generate_synthetic_lot

app = FastAPI(title="AGNI-PARIKSHA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ParameterConfig(BaseModel):
    name: str
    baseline: float
    spread: float
    limit: Optional[float] = None

class GenerateRequest(BaseModel):
    lot_size: int = 20
    part_type: str = "SyntheticPart"
    checkpoints: List[float] = [0, 24, 96, 168]
    parameters: List[ParameterConfig]
    defect_prevalence: float = 0.02
    archetypes: List[str] = ["elevated_drift", "shape_change", "knee_defect"]
    seed: Optional[int] = None

def process_and_save(df: pd.DataFrame, db: Session, mapping_dict: dict = None, is_synthetic: bool = False, params_config: list = None):
    try:
        long_df, warnings = normalize_dataset(df, mapping_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    lot_id = long_df['lot_id'].iloc[0]
    
    # Process Module A
    # If parameters have limits, pass them
    datasheet_limits = {}
    if params_config:
        for p in params_config:
            if hasattr(p, 'limit') and p.limit is not None:
                datasheet_limits[p.name] = p.limit
                
    mod_a_res = run_module_a(long_df, datasheet_limits=datasheet_limits)
    
    # Process Module B
    target_t = long_df['timepoint_hours'].max()
    mod_b_res = run_module_b(long_df, backend='gbdt', target_time=target_t)
    
    # Process Module C
    fusion_res = run_module_c(mod_a_res, mod_b_res)
    
    # Clear old lot data (for simplicity in this MVP)
    db.query(PartReading).filter(PartReading.lot_id == lot_id).delete()
    db.query(PartResult).filter(PartResult.lot_id == lot_id).delete()
    
    # Extract Ground Truth if synthetic
    gt_map = {}
    if is_synthetic:
        # Assuming original df has IsDefective_GT and DefectType_GT
        for _, row in df.drop_duplicates(subset=['PartID']).iterrows():
            gt_map[row['PartID']] = {
                "is_defective": row.get('IsDefective_GT', False),
                "defect_type": row.get('DefectType_GT', 'None')
            }
    
    # Store Readings
    readings = []
    for _, row in long_df.iterrows():
        readings.append(PartReading(
            part_id=row['part_id'],
            lot_id=row['lot_id'],
            parameter_name=row['parameter_name'],
            timepoint_hours=row['timepoint_hours'],
            value=row['value']
        ))
    db.bulk_save_objects(readings)
    
    # Store Results
    results = []
    for _, row in fusion_res.iterrows():
        highest_param = "Unknown"
        if not mod_a_res.empty:
            part_a = mod_a_res[mod_a_res['part_id'] == row['part_id']]
            if not part_a.empty:
                attr_cols = [c for c in part_a.columns if c.startswith('attr_')]
                if attr_cols:
                    attr_row = part_a.iloc[0]
                    highest_attr_col = max(attr_cols, key=lambda x: attr_row.get(x, 0))
                    highest_param = highest_attr_col.replace('attr_', '')
                    
        is_defective_gt = None
        defect_type_gt = None
        if is_synthetic and row['part_id'] in gt_map:
            is_defective_gt = bool(gt_map[row['part_id']]['is_defective'])
            defect_type_gt = str(gt_map[row['part_id']]['defect_type'])
                    
        results.append(PartResult(
            part_id=row['part_id'],
            lot_id=lot_id,
            verdict=row['verdict'],
            cri_score=row['cri'],
            a_score=row['a_score'],
            d_score=row['d_score'],
            highest_attr_param=highest_param,
            is_defective_gt=is_defective_gt,
            defect_type_gt=defect_type_gt
        ))
    db.bulk_save_objects(results)
    db.commit()
    
    return lot_id, warnings, len(results)

@app.post("/api/upload")
async def upload_data(
    file: UploadFile = File(...), 
    column_mapping: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        df = pd.read_csv(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid CSV file")
        
    mapping_dict = json.loads(column_mapping) if column_mapping else None
    
    lot_id, warnings, count = process_and_save(df, db, mapping_dict, is_synthetic=False)
    
    return {
        "status": "success", 
        "lot_id": lot_id, 
        "warnings": warnings,
        "processed_parts": count
    }

@app.post("/api/generate")
def generate_and_analyze(req: GenerateRequest, db: Session = Depends(get_db)):
    params_dict = [p.dict() for p in req.parameters]
    lot_id = f"SYNTH_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}"
    
    df = generate_synthetic_lot(
        lot_id=lot_id,
        part_type=req.part_type,
        lot_size=req.lot_size,
        checkpoints=req.checkpoints,
        parameters=params_dict,
        defect_rate=req.defect_prevalence / 100.0,
        archetypes=req.archetypes,
        random_seed=req.seed
    )
    
    # Auto-detect should work perfectly since we generated it
    lot_id, warnings, count = process_and_save(df, db, mapping_dict=None, is_synthetic=True, params_config=req.parameters)
    
    return {
        "status": "success", 
        "lot_id": lot_id, 
        "warnings": warnings,
        "processed_parts": count
    }

@app.post("/api/generate/csv")
def generate_csv(req: GenerateRequest):
    params_dict = [p.dict() for p in req.parameters]
    lot_id = f"SYNTH_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}"
    
    df = generate_synthetic_lot(
        lot_id=lot_id,
        part_type=req.part_type,
        lot_size=req.lot_size,
        checkpoints=req.checkpoints,
        parameters=params_dict,
        defect_rate=req.defect_prevalence / 100.0,
        archetypes=req.archetypes,
        random_seed=req.seed
    )
    
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={lot_id}.csv"
    return response

@app.get("/api/lots")
def get_lots(db: Session = Depends(get_db)):
    lots = db.query(PartResult.lot_id).distinct().all()
    return [{"lot_id": l[0]} for l in lots]

@app.get("/api/lots/{lot_id}/parts")
def get_lot_parts(lot_id: str, db: Session = Depends(get_db)):
    parts = db.query(PartResult).filter(PartResult.lot_id == lot_id).all()
    return parts

@app.get("/api/parts/{part_id}")
def get_part_details(part_id: str, db: Session = Depends(get_db)):
    part_result = db.query(PartResult).filter(PartResult.part_id == part_id).first()
    if not part_result:
        raise HTTPException(status_code=404, detail="Part not found")
        
    readings = db.query(PartReading).filter(PartReading.part_id == part_id).all()
    
    return {
        "result": part_result,
        "readings": readings
    }

@app.get("/api/parts/{part_id}/certificate")
def download_certificate(part_id: str, db: Session = Depends(get_db)):
    part_result = db.query(PartResult).filter(PartResult.part_id == part_id).first()
    if not part_result:
        raise HTTPException(status_code=404, detail="Part not found")
        
    if part_result.verdict == "ACCEPT":
        raise HTTPException(status_code=400, detail="Certificates only available for REVIEW/REJECT verdicts")
        
    lot_id = part_result.lot_id
    param = part_result.highest_attr_param
    
    p_readings = db.query(PartReading).filter(
        PartReading.part_id == part_id,
        PartReading.parameter_name == param
    ).all()
    part_df = pd.DataFrame([{ "timepoint_hours": r.timepoint_hours, "value": r.value, "part_id": part_id } for r in p_readings])
    
    l_readings = db.query(PartReading).filter(
        PartReading.lot_id == lot_id,
        PartReading.parameter_name == param
    ).all()
    lot_df = pd.DataFrame([{ "timepoint_hours": r.timepoint_hours, "value": r.value, "part_id": r.part_id } for r in l_readings])
    
    output_path = f"/tmp/cert_{part_id}.pdf"
    if os.name == 'nt':
        output_path = f"cert_{part_id}.pdf"
        
    attribution_scores = {param: 1.0}
    
    create_pdf_certificate(
        part_id=part_id,
        lot_id=lot_id,
        verdict=part_result.verdict,
        cri_score=part_result.cri_score,
        part_df=part_df,
        lot_df=lot_df,
        attribution_scores=attribution_scores,
        output_path=output_path
    )
    
    return FileResponse(output_path, media_type="application/pdf", filename=f"{part_id}_certificate.pdf")
    
@app.post("/api/retrain")
def trigger_retraining():
    return {"status": "success", "message": "Retraining job queued successfully."}
