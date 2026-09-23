import pandas as pd
import json
from agnipariksha.config import FAMILY_SPECS
from agnipariksha.module_a.outlier import DynamicOutlierDetector
from agnipariksha.module_b.predictor import DriftPredictor
from agnipariksha.evaluation.evaluator import AgniEvaluator

df_main = pd.read_csv("data/dataset.csv")
with open("data/manifest.json", "r") as f: manifest = json.load(f)
train_lots = [item['lot_id'] for item in manifest['TRAIN']]
cal_lots = [item['lot_id'] for item in manifest['CALIBRATION']]
dev_lots = [item['lot_id'] for item in manifest['DEVELOPMENT']]
df_train = df_main[df_main['lot_id'].isin(train_lots)]
df_cal = df_main[df_main['lot_id'].isin(cal_lots)]
df_dev = df_main[df_main['lot_id'].isin(dev_lots)]

module_b = DriftPredictor()
module_b.fit(df_train, df_cal)
module_a = DynamicOutlierDetector()
evaluator = AgniEvaluator()

df_prev = evaluator.evaluate_prevalence(df_dev, module_a, module_b, prevalence_rates=[0.005, 0.05], k_noise=3.5)
print(df_prev)

# Calculate B2 score
for idx, row in df_prev.iterrows():
    n_total = row['N']
    n_def = row['n_def']
    n_neg = n_total - n_def
    
    # parse recall and fpr
    rec_str = row['Recall (bound)'].split('%')[0]
    fpr_str = row['FPR (bound)'].split('%')[0]
    recall = float(rec_str) / 100
    fpr = float(fpr_str) / 100
    
    tp = recall * n_def
    fn = n_def - tp
    fp = fpr * n_neg
    
    score10 = evaluator.calculate_score(fp, fn, n_total, w_fn=10)
    score50 = evaluator.calculate_score(fp, fn, n_total, w_fn=50)
    score100 = evaluator.calculate_score(fp, fn, n_total, w_fn=100)
    print(f"Prevalence {row['Prevalence']} | Sc10: {score10:.1f} | Sc50: {score50:.1f} | Sc100: {score100:.1f}")

