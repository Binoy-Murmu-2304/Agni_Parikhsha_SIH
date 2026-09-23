import os
with open('agnipariksha/api/main.py', 'r') as f:
    c = f.read()

old_func = '''@app.get("/components/{id}/card")
def get_component_card(id: str):
    df_c = df_cache[df_cache['component_id'] == id]
    if len(df_c) == 0:
        raise HTTPException(404, "Component not found")
    row = df_c.iloc[0]
    md = qa_gen.generate_card(
        comp_id=row['component_id'],
        family=row['family'],
        verdict=row['disposition'],
        risk_tier=row.get('risk_tier', 'HIGH'),
        measured_24h=row.get('value_24h', 0.0),
        pred_168h=row.get('pred_168h', 0.0),
        margin=(row.get('allowed_slope', 0.0) - row.get('measured_slope', 0.0)),
        conformal_90=row.get('conformal_radius_90', 0.0),
        module_a_outlier=bool(row.get('trigger_module_a', 0)),
        safety_slope_breach=bool(row.get('trigger_safety_slope', 0)),
        capability_fallback=row.get('disposition') == 'FULL_BURN_IN'
    )
    return {"markdown": md}'''

new_func = '''@app.get("/components/{id}/card")
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
        explanation={'feature_importance': {}},
        explainer=None
    )
    return {"markdown": md}'''

c = c.replace(old_func, new_func)
with open('agnipariksha/api/main.py', 'w') as f:
    f.write(c)
