import os

with open('agnipariksha/api/main.py', 'r') as f:
    c = f.read()

replacement = '''    df_res = pd.concat(res)
    
    # API Doctrine: Enforce capability routing strictly. 
    # Failing families must be FULL_BURN_IN, never GREEN or RED at 24h.
    def enforce_api_routing(row):
        if CAPABILITY_ROUTING.get(row['family']) == 'MANDATORY_FULL_BURN_IN':
            return 'FULL_BURN_IN'
        return row['disposition']
    df_res['disposition'] = df_res.apply(enforce_api_routing, axis=1)
    
    def map_risk(d):'''

c = c.replace('''    df_res = pd.concat(res)
    def map_risk(d):''', replacement)

with open('agnipariksha/api/main.py', 'w') as f:
    f.write(c)
