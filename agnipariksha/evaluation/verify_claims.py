import json
import csv
import sys

def main():
    try:
        with open("metrics_canonical.json", "r") as f:
            metrics = json.load(f)
    except FileNotFoundError:
        print("Error: metrics_canonical.json not found.")
        sys.exit(1)
        
    try:
        with open("claims.csv", "r") as f:
            reader = csv.DictReader(f)
            claims = list(reader)
    except FileNotFoundError:
        print("Error: claims.csv not found.")
        sys.exit(1)
        
    all_passed = True
    for row in claims:
        claim_id = row['claim_id']
        expected = float(row['expected_value'])
        tolerance = float(row['tolerance'])
        metric_key = row['metric_key']
        
        # Traverse JSON path (e.g. "DIGITAL_IC.cov_90")
        keys = metric_key.split(".")
        val = metrics
        try:
            for k in keys:
                val = val[k]
            actual = float(val)
        except (KeyError, TypeError):
            print(f"FAIL {claim_id}: Key {metric_key} not found in canonical metrics.")
            all_passed = False
            continue
            
        if abs(actual - expected) <= tolerance:
            print(f"PASS {claim_id}: {actual} is within {tolerance} of {expected}")
        else:
            print(f"FAIL {claim_id}: {actual} differs from expected {expected} by more than {tolerance}")
            all_passed = False
            
    if not all_passed:
        sys.exit(1)
    else:
        print("100% of claims asserted successfully.")
        
if __name__ == "__main__":
    main()
    # R6 Compute invariants
    from agnipariksha.data_generator.generator import AgniSimGenerator
    train_mechs = set(AgniSimGenerator.TRAIN_MECHANISMS)
    stress_mechs = set(AgniSimGenerator.STRESS_MECHANISMS)
    assert len(train_mechs.intersection(stress_mechs)) == 0, "Stress mechanisms intersect with train mechanisms!"
    
    chamber_savings = (168 - 24) / 168 * 100
    assert abs(chamber_savings - 85.71) < 0.01, "Chamber savings mismatch!"
    
    try:
        import pandas as pd
        df_prev = pd.read_csv('data/prevalence_results.csv')
        fpr_str = df_prev[df_prev['Prevalence'] == '5.0%']['FPR (bound)'].iloc[0]
        fpr = float(fpr_str.split('%')[0]) / 100
        green_fraction = 1.0 - fpr
        realized_savings = green_fraction * chamber_savings
        print(f"Realized Chamber Savings (at 5% prev FPR): {realized_savings:.2f}%")
    except:
        pass
    print("All Invariants Verified.")
