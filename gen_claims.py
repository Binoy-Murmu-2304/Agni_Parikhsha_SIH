import json
import csv

with open('metrics_canonical.json', 'r') as f:
    metrics = json.load(f)

claims = []
for family, data in metrics.items():
    for metric, value in data.items():
        if isinstance(value, float):
            claims.append({
                'claim_id': f"{family}_{metric}",
                'expected_value': f"{value:.4f}",
                'tolerance': "0.01",
                'metric_key': f"{family}.{metric}",
                'verification_command': "python -m agnipariksha.evaluation.verify_claims"
            })
            
with open('claims.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['claim_id', 'expected_value', 'tolerance', 'metric_key', 'verification_command'])
    writer.writeheader()
    writer.writerows(claims)
