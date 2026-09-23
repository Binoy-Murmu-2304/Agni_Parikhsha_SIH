import pandas as pd
from agnipariksha.evaluation.evaluator import AgniEvaluator

df = pd.read_csv("data/prevalence_results.csv")
evaluator = AgniEvaluator()

sensitivity = []
for idx, row in df.iterrows():
    # Back-calculate FP and FN from rates
    n_total = row['N']
    n_def = row['n_def']
    n_neg = n_total - n_def
    
    # FPR is a string like "10.00% [9.5%, 10.5%]"
    fpr_str = str(row['FPR (bound)']).split('%')[0]
    try: fpr = float(fpr_str) / 100.0
    except ValueError: fpr = 0.0
    fp = int(fpr * n_neg)
    
    recall_str = str(row['Recall (bound)']).split('%')[0]
    try: recall = float(recall_str) / 100.0
    except ValueError: recall = 0.0
    fn = int((1 - recall) * n_def)
    
    scores = {}
    for w_fn in [10, 50, 100]:
        scores[f"Score (w_FN={w_fn})"] = evaluator.calculate_score(fp, fn, n_total, w_fn)
        
    sensitivity.append({
        "Prevalence": row['Prevalence'],
        **scores
    })
    
df_sens = pd.DataFrame(sensitivity)
print("\nw_FN Sensitivity Table:")
print(df_sens.to_string(index=False))
df_sens.to_csv("data/w_fn_sensitivity.csv", index=False)
