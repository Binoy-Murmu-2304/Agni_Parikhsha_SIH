import json
with open('data/manifest.json', 'r') as f:
    manifest = json.load(f)
manifest['DEVELOPMENT'] = manifest.pop('BLIND_TEST')

# generate fresh FINAL_EVAL
# We had 50 lots total (60/20/20 splits -> 30, 10, 10 lots)
# Let's add 10 new lots for FINAL_EVAL
import sys
sys.path.append('.')
from agnipariksha.data_generator.generator import AgniSimGenerator
from agnipariksha.config import FAMILY_SPECS
import pandas as pd

gen = AgniSimGenerator(seed=43) # fresh seed for FINAL_EVAL
final_eval_lots = []
final_eval_data = []

lot_idx = 50
for _ in range(10): # 10 lots
    family = list(FAMILY_SPECS.keys())[lot_idx % len(FAMILY_SPECS)]
    lot_id = f"FINAL_LOT_{lot_idx:04d}"
    
    df_lot = gen.generate_lot(lot_id, family)
    final_eval_data.append(df_lot)
    
    final_eval_lots.append({
        "lot_id": lot_id,
        "family": family,
        "size": len(df_lot)
    })
    lot_idx += 1

manifest['FINAL_EVAL'] = final_eval_lots

with open('data/manifest.json', 'w') as f:
    json.dump(manifest, f, indent=2)

df_final = pd.concat(final_eval_data)
df_main = pd.read_csv('data/dataset.csv')
df_new = pd.concat([df_main, df_final])
df_new.to_csv('data/dataset.csv', index=False)
print("Saved FINAL_EVAL to dataset.csv and updated manifest.json")
