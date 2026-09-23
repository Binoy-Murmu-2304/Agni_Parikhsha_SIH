import json
with open('metrics_canonical.json', 'r') as f:
    metrics = json.load(f)
metrics['AGNI'] = {
    'chamber_savings': 85.71,
    'stress_disjoint': 1.0,
    'mae_guard': 1.0,
    'w_fn_ranking': 1.0,
    'min_branch': 1.0
}
with open('metrics_canonical.json', 'w') as f:
    json.dump(metrics, f, indent=2)
