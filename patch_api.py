import os

with open('agnipariksha/api/main.py', 'r') as f:
    c = f.read()

c = c.replace('df_res.to_dict(orient="records")', 'df_res.fillna(0.0).to_dict(orient="records")')
c = c.replace("row.get('conformal_radius_95', 0.0)", "row.get('conformal_radius_95', 0.0) if pd.notna(row.get('conformal_radius_95')) else 0.0")

with open('agnipariksha/api/main.py', 'w') as f:
    f.write(c)
