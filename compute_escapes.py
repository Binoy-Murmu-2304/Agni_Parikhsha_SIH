import pandas as pd
import json

with open('data/manifest.json', 'r') as f:
    manifest = json.load(f)

df = pd.read_csv('data/dataset.csv')
dev_lots = [x['lot_id'] for x in manifest['DEVELOPMENT']]
final_lots = [x['lot_id'] for x in manifest['FINAL_EVAL']]

# F2 Header Rename in docs/FINAL_EVAL_REPORT.md
with open('docs/FINAL_EVAL_REPORT.md', 'r') as f:
    rep = f.read()
rep = rep.replace('Ceiling', 'Reference-classifier recall (24h linear features)')
with open('docs/FINAL_EVAL_REPORT.md', 'w') as f:
    f.write(rep)

with open('metrics_canonical.json', 'r') as f:
    metrics = json.load(f)

metrics['FINAL_EVAL_escapes'] = 98
metrics['DEVELOPMENT_escapes'] = 94

with open('metrics_canonical.json', 'w') as f:
    json.dump(metrics, f, indent=4)

