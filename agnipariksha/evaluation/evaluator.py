import pandas as pd
from typing import Dict, Any

from agnipariksha.config import FAMILY_SPECS, DEFAULT_W_FN

class AgniEvaluator:
    def __init__(self, w_fp: float = 1.0, w_fn: float = DEFAULT_W_FN):
        self.w_fp = w_fp
        self.w_fn = w_fn
        
    def end_to_end_disposition(self, df_lot: pd.DataFrame, module_a, module_b, k_noise: float = 3.5) -> pd.DataFrame:
        df = df_lot.copy()
        df_a = module_a.detect_univariate(df, 'value_24h')
        df_b = module_b.compute_safety_slope(df_a, current_hour=24, k_noise=k_noise)
        
        def conformal_breach(row):
            if 'pred_168h' in row and 'conformal_radius_90' in row:
                if row['pred_168h'] + row['conformal_radius_90'] > FAMILY_SPECS[row['family']]['spec_max']:
                    return 1
            return 0
        df_b['trigger_conformal'] = df_b.apply(conformal_breach, axis=1)
        
        df_b['trigger_safety_slope'] = (df_b[['measured_slope', 'pred_slope']].max(axis=1) > (df_b['allowed_slope'] + df_b.get('slope_tolerance', 0))).astype(int)
        df_b['trigger_lot_stat'] = (df_b[['measured_slope', 'pred_slope']].max(axis=1) > df_b['lot_stat_bound']).astype(int)
        df_b['trigger_module_a'] = df_b['module_a_verdict'].apply(lambda x: 1 if "RED" in str(x) else 0)
        
        def evaluate_final(row):
            if row['trigger_module_a'] == 1: return 1
            if row['trigger_safety_slope'] == 1: return 1
            # ConfBreach fires 0%, removed from final_flag as per F4
            return 0
            
        df_b['final_flag'] = df_b.apply(evaluate_final, axis=1)
        return df_b

    def calculate_score(self, fp, fn, n_total, w_fn=None):
        w_fn_used = w_fn if w_fn is not None else self.w_fn
        penalty = (100.0 / n_total) * (self.w_fp * fp + w_fn_used * fn)
        return max(0.0, 100.0 - penalty)
        
    def evaluate_prevalence(self, df_population: pd.DataFrame, module_a, module_b, prevalence_rates: list, k_noise: float = 3.5) -> pd.DataFrame:
        results = []
        for rate in prevalence_rates:
            dfs_res = []
            # F1: Group by lot_id
            for lot_id, lot_data in df_population.groupby('lot_id'):
                fam = lot_data['family'].iloc[0]
                df_neg_pool = lot_data[lot_data['is_defective'] == 0]
                
                n_neg = len(df_neg_pool)
                n_def = int(round(n_neg * rate / (1 - rate)))
                n_total = n_neg + n_def
                
                df_neg = df_neg_pool # use all healthy parts in the lot
                
                df_fam_pool = df_population[df_population['family'] == fam]
                df_def_pool = df_fam_pool[df_fam_pool['is_defective'] == 1]
                if len(df_def_pool) < n_def:
                    raise ValueError(f"Insufficient defectives in family {fam}")
                df_def = df_def_pool.sample(n=n_def, random_state=42)
                
                df_eval = pd.concat([df_def, df_neg]).reset_index(drop=True)
                dfs_res.append(self.end_to_end_disposition(df_eval, module_a, module_b, k_noise=k_noise))
                
            df_res = pd.concat(dfs_res)
            
            n_total = len(df_res)
            tp = len(df_res[(df_res['is_defective'] == 1) & (df_res['final_flag'] == 1)])
            fn = len(df_res[(df_res['is_defective'] == 1) & (df_res['final_flag'] == 0)])
            fp = len(df_res[(df_res['is_defective'] == 0) & (df_res['final_flag'] == 1)])
            tn = len(df_res[(df_res['is_defective'] == 0) & (df_res['final_flag'] == 0)])
            n_def_actual = tp + fn
            n_neg_actual = fp + tn
            recall = tp / max(1, n_def_actual)
            fpr = fp / max(1, n_neg_actual)
            precision = tp / max(1, tp + fp)
            fw_1000 = (fp / max(1, n_neg_actual)) * 1000
            
            try:
                from statsmodels.stats.proportion import proportion_confint
                rec_ci = proportion_confint(tp, n_def_actual, alpha=0.05, method='beta')
                fpr_ci = proportion_confint(fp, n_neg_actual, alpha=0.05, method='beta')
            except ImportError:
                import scipy.stats as stats
                def prop_ci(k, n, alpha=0.05):
                    lower = stats.beta.ppf(alpha/2, k, n-k+1) if k > 0 else 0
                    upper = stats.beta.ppf(1-alpha/2, k+1, n-k) if k < n else 1
                    return lower, upper
                rec_ci = prop_ci(tp, n_def_actual, alpha=0.05)
                fpr_ci = prop_ci(fp, n_neg_actual, alpha=0.05)
                
            results.append({
                "Prevalence": f"{rate*100:.1f}%",
                "N": n_total,
                "n_def": n_def_actual,
                "Recall (bound)": f"{recall*100:.2f}% [{rec_ci[0]*100:.2f}%, {rec_ci[1]*100:.2f}%]",
                "FPR (bound)": f"{fpr*100:.2f}% [{fpr_ci[0]*100:.2f}%, {fpr_ci[1]*100:.2f}%]",
                "Precision": f"{precision*100:.2f}%",
                "False Withdrawals / 1000": round(fw_1000, 1),
                "Provenance": "DEVELOPMENT"
            })
        return pd.DataFrame(results)

    def conformal_coverage_audit(self, df_blind: pd.DataFrame, module_b) -> Dict[str, Any]:
        results = {}
        import scipy.stats as stats
        def prop_ci(k, n, alpha=0.05):
            lower = stats.beta.ppf(alpha/2, k, n-k+1) if k > 0 else 0
            upper = stats.beta.ppf(1-alpha/2, k+1, n-k) if k < n else 1
            return lower, upper
        for family in df_blind['family'].unique():
            df_f = df_blind[df_blind['family'] == family]
            preds = module_b.predict_with_conformal(df_f, family)
            err = (df_f['value_168h'] - preds['pred_168h']).abs()
            cov_90 = (err <= preds['conformal_radius_90']).mean()
            cov_95 = (err <= preds['conformal_radius_95']).mean()
            mae = err.mean()
            n = len(df_f)
            # F3: use finite-sample quantile level in documentation. Our formula is fine here since we just measure empirical coverage.
            ci_90 = prop_ci(int(cov_90 * n), n, 0.10)
            ci_95 = prop_ci(int(cov_95 * n), n, 0.05)
            results[family] = {
                "MAE": float(mae),
                "cov_90": float(cov_90),
                "cov_90_CI": [float(ci_90[0]), float(ci_90[1])],
                "cov_95": float(cov_95),
                "cov_95_CI": [float(ci_95[0]), float(ci_95[1])],
                "n": n
            }
        return results
