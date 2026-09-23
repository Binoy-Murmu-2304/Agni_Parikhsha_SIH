import os
with open('agnipariksha/api/main.py', 'r') as f:
    c = f.read()

old = '''    df_res = evaluator.end_to_end_disposition(df, mod_a, mod_b, k_noise=3.5)
    def map_risk(d):'''

new = '''    res = []
    for lot_id, lot_data in df.groupby('lot_id'):
        res.append(evaluator.end_to_end_disposition(lot_data, mod_a, mod_b, k_noise=3.5))
    df_res = pd.concat(res)
    def map_risk(d):'''

c = c.replace(old, new)
with open('agnipariksha/api/main.py', 'w') as f:
    f.write(c)
