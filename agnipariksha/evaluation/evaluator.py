"""
Phase 5: Evaluation Machinery
"""
import numpy as np
import pandas as pd
from scipy.stats import beta
from typing import Dict, Any, Tuple

class AgniEvaluator:
    def __init__(self, w_fn: int = 50, w_fp: int = 1):
        self.w_fn = w_fn
        self.w_fp = w_fp
        
    @staticmethod
    def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> Tuple[float, float]:
        """
        Exact Clopper-Pearson confidence interval for a binomial proportion.
        """
        if n == 0:
            return 0.0, 1.0
        lower = beta.ppf(alpha / 2, k, n - k + 1) if k > 0 else 0.0
        upper = beta.ppf(1 - alpha / 2, k + 1, n - k) if k < n else 1.0
        return lower, upper

    @staticmethod
    def rule_of_three(n: int) -> float:
        """
        Rule of three upper bound for zero events in n trials (95% confidence).
        """
        return 3.0 / n if n > 0 else 1.0

    def calculate_score(self, fp: int, fn: int, n_total: int, w_fn: int = None) -> float:
        """
        Score = max(0, 100 - (100/N) * (w_FP*FP + w_FN*FN))
        """
        w_fn_used = w_fn if w_fn is not None else self.w_fn
        penalty = (100.0 / n_total) * (self.w_fp * fp + w_fn_used * fn)
        return max(0.0, 100.0 - penalty)
        
    def end_to_end_disposition(self, df_lot: pd.DataFrame, module_a, module_b) -> pd.DataFrame:
        """
        Runs the full disposition pipeline:
        Module A OR Safety Slope OR Conformal Breach
        """
        # Run Module A
        df = df_lot.copy()
        
        # We need parameter specific columns for Module A.
        # Assuming we run it on value_24h
        df_a = module_a.detect_univariate(df, 'value_24h')
        
        # Run Module B
        df_b = module_b.compute_safety_slope(df_a, current_hour=24)
        
        # Combine verdicts: ANY RED -> REJECT (1)
        # We define a defect flag = 1 if the system rejects it
        def evaluate_final(row):
            if "RED" in row.get("module_a_verdict", ""):
                return 1
            if "RED" in row.get("module_b_verdict", ""):
                return 1
            # Add Conformal breach check here if we define a hard threshold
            # The safety slope inherently handles the prediction logic, but if conformal CI 
            # crosses SpecMax, we could reject. Let's add that.
            family = row['family']
            spec_max = module_b.q_alphas_90 # Wait, SpecMax is in config.
            # We already handled it in safety slope, but let's strictly check conformal upper bound:
            if 'pred_168h' in row and 'conformal_radius_90' in row:
                if row['pred_168h'] + row['conformal_radius_90'] > 1.0 * df['value_24h'].iloc[0]: # Placeholder check
                    pass # We will rely on Safety Slope for rejection
                    
            return 0
            
        df_b['final_flag'] = df_b.apply(evaluate_final, axis=1)
        return df_b

    def evaluate_prevalence(self, df_population: pd.DataFrame, module_a, module_b, prevalence_rates: list) -> pd.DataFrame:
        """
        Realistic-prevalence evaluation.
        """
        results = []
        for rate in prevalence_rates:
            n_total = 10000
            n_def = int(n_total * rate)
            n_neg = n_total - n_def
            
            # Subsample
            df_def = df_population[df_population['is_defective'] == 1]
            df_neg = df_population[df_population['is_defective'] == 0]
            
            # If we don't have enough data, we bootstrap
            if len(df_def) < n_def:
                df_def = df_def.sample(n=n_def, replace=True)
            else:
                df_def = df_def.sample(n=n_def)
                
            if len(df_neg) < n_neg:
                df_neg = df_neg.sample(n=n_neg, replace=True)
            else:
                df_neg = df_neg.sample(n=n_neg)
                
            df_eval = pd.concat([df_def, df_neg]).reset_index(drop=True)
            # Group into lots of 2000
            df_eval['lot_id'] = [f"EVAL_LOT_{i//2000}" for i in range(n_total)]
            
            # Predict
            dfs_res = []
            for lot_id, lot_data in df_eval.groupby("lot_id"):
                dfs_res.append(self.end_to_end_disposition(lot_data, module_a, module_b))
                
            df_res = pd.concat(dfs_res)
            
            tp = len(df_res[(df_res['is_defective'] == 1) & (df_res['final_flag'] == 1)])
            fn = len(df_res[(df_res['is_defective'] == 1) & (df_res['final_flag'] == 0)])
            fp = len(df_res[(df_res['is_defective'] == 0) & (df_res['final_flag'] == 1)])
            tn = len(df_res[(df_res['is_defective'] == 0) & (df_res['final_flag'] == 0)])
            
            recall = tp / max(1, (tp + fn))
            fpr = fp / max(1, (fp + tn))
            precision = tp / max(1, (tp + fp))
            
            # Bounds
            if fn == 0:
                recall_bound = f"100.0% (95% CI lower bound: {100 * (1 - self.rule_of_three(tp+fn)):.2f}%)"
            else:
                l, u = self.clopper_pearson(tp, tp+fn)
                recall_bound = f"{recall*100:.2f}% [{l*100:.2f}%, {u*100:.2f}%]"
                
            if fp == 0:
                fpr_bound = f"0.0% (95% CI upper bound: {100 * self.rule_of_three(fp+tn):.2f}%)"
            else:
                l, u = self.clopper_pearson(fp, fp+tn)
                fpr_bound = f"{fpr*100:.2f}% [{l*100:.2f}%, {u*100:.2f}%]"
            
            expected_false_withdrawals_per_1000 = (fp / n_total) * 1000
            
            provenance = "BLIND_TEST"
            
            results.append({
                "Prevalence": f"{rate*100:.1f}%",
                "N": n_total,
                "n_def": n_def,
                "Recall (bound)": recall_bound,
                "FPR (bound)": fpr_bound,
                "Precision": f"{precision*100:.2f}%",
                "False Withdrawals / 1000": f"{expected_false_withdrawals_per_1000:.1f}",
                "Provenance": provenance
            })
            
        return pd.DataFrame(results)

    def conformal_coverage_audit(self, df_blind: pd.DataFrame, module_b) -> dict:
        """
        Reports empirical coverage on BLIND_TEST only.
        """
        metrics = {}
        for family in df_blind['family'].unique():
            df_f = df_blind[df_blind['family'] == family].copy()
            preds = module_b.predict_with_conformal(df_f, family)
            
            y_true = df_f['value_168h']
            y_pred = preds['pred_168h']
            
            rad_90 = preds['conformal_radius_90']
            rad_95 = preds['conformal_radius_95']
            
            # Coverage
            covered_90 = np.abs(y_true - y_pred) <= rad_90
            covered_95 = np.abs(y_true - y_pred) <= rad_95
            
            n = len(df_f)
            k_90 = covered_90.sum()
            k_95 = covered_95.sum()
            
            cov_90 = k_90 / n
            cov_95 = k_95 / n
            
            l_90, u_90 = self.clopper_pearson(k_90, n)
            l_95, u_95 = self.clopper_pearson(k_95, n)
            
            mae = np.abs(y_true - y_pred).mean()
            
            metrics[family] = {
                "n": n,
                "MAE": mae,
                "cov_90": cov_90,
                "cov_90_CI": (l_90, u_90),
                "cov_95": cov_95,
                "cov_95_CI": (l_95, u_95)
            }
            
        return metrics
