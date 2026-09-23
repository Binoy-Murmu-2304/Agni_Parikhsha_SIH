import os

with open('agnipariksha/api/main.py', 'r') as f:
    c = f.read()

replacement = '''
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
'''
old = '''
    df_res['risk_tier'] = df_res['disposition'].apply(map_risk)
    return df_res.where(pd.notnull(df_res), None).to_dict(orient="records")
'''
c = c.replace(old.strip(), replacement.strip())

with open('agnipariksha/api/main.py', 'w') as f:
    f.write(c)
