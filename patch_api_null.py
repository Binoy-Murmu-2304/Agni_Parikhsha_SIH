import os

with open('agnipariksha/api/main.py', 'r') as f:
    c = f.read()

replacement = '''
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
    }'''

c = c.replace('''
    return {
        "component_id": row['component_id'],
        "disposition": row['disposition'],
        "pred_168h": row.get('pred_168h', 0.0),
        "conformal_interval_95": row.get('conformal_radius_95', 0.0),
        "safety_slope_margin": row.get('allowed_slope', 0.0) - row.get('measured_slope', 0.0),
        "measured_slope": row.get('measured_slope', 0.0),
        "allowed_slope": row.get('allowed_slope', 0.0),
        "trigger_module_a": row.get('trigger_module_a', 0),
        "trigger_safety_slope": row.get('trigger_safety_slope', 0),
    }''', replacement)

with open('agnipariksha/api/main.py', 'w') as f:
    f.write(c)
