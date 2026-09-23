import json
import pandas as pd
import numpy as np
import os
from agnipariksha.module_a.outlier import DynamicOutlierDetector
from agnipariksha.module_b.predictor import DriftPredictor
from agnipariksha.evaluation.evaluator import AgniEvaluator
from agnipariksha.evaluation.stress_tester import StressTester
from agnipariksha.config import FAMILY_SPECS

def main():
    print("Loading data...")
    df_main = pd.read_csv("data/dataset.csv")
    df_stress = pd.read_csv("data/stress_set.csv")
    
    with open("data/manifest.json", "r") as f:
        manifest = json.load(f)
        
    train_lots = [item['lot_id'] for item in manifest['TRAIN']]
    cal_lots = [item['lot_id'] for item in manifest['CALIBRATION']]
    blind_lots = [item['lot_id'] for item in manifest['BLIND_TEST']]
    
    df_train = df_main[df_main['lot_id'].isin(train_lots)]
    df_cal = df_main[df_main['lot_id'].isin(cal_lots)]
    df_blind = df_main[df_main['lot_id'].isin(blind_lots)]
    
    print("Initializing and fitting Module B...")
    module_b = DriftPredictor()
    module_b.fit(df_train, df_cal)
    
    module_a = DynamicOutlierDetector()
    evaluator = AgniEvaluator()
    
    metrics = {}
    
    print("Running Conformal Coverage Audit on BLIND_TEST...")
    coverage_metrics = evaluator.conformal_coverage_audit(df_blind, module_b)
    
    for family, m in coverage_metrics.items():
        metrics[family] = {
            "MAE": m["MAE"],
            "cov_90": m["cov_90"],
            "cov_90_CI_lower": m["cov_90_CI"][0],
            "cov_90_CI_upper": m["cov_90_CI"][1],
            "cov_95": m["cov_95"],
            "cov_95_CI_lower": m["cov_95_CI"][0],
            "cov_95_CI_upper": m["cov_95_CI"][1],
            "n": m["n"]
        }
    
    print("Running Prevalence Evaluation...")
    # Prevalence sweep on BLIND_TEST
    df_prev = evaluator.evaluate_prevalence(df_blind, module_a, module_b, prevalence_rates=[0.001, 0.005, 0.01, 0.05])
    df_prev.to_csv("data/prevalence_results.csv", index=False)
    
    # Threshold sweep logic placeholder (could just be varying z_yellow and measuring score)
    
    print("Running Stress Test...")
    stress_tester = StressTester(evaluator, module_a, module_b)
    stress_res = stress_tester.evaluate_stress_set(df_stress)
    
    # Save canonical metrics
    with open("metrics_canonical.json", "w") as f:
        json.dump(metrics, f, indent=2)
        
    print("Evaluation Complete.")
    
if __name__ == "__main__":
    main()
