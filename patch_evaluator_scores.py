import os

with open('agnipariksha/evaluation/evaluator.py', 'r') as f:
    content = f.read()

replacement = '''
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
                
            sc10 = self.calculate_score(fp, fn, n_total, w_fn=10)
            sc50 = self.calculate_score(fp, fn, n_total, w_fn=50)
            sc100 = self.calculate_score(fp, fn, n_total, w_fn=100)
            
            results.append({
                "Prevalence": f"{rate*100:.1f}%",
                "N": n_total,
                "n_def": n_def_actual,
                "TP": tp,
                "FN": fn,
                "FP": fp,
                "Recall (bound)": f"{recall*100:.2f}% [{rec_ci[0]*100:.2f}%, {rec_ci[1]*100:.2f}%]",
                "FPR (bound)": f"{fpr*100:.2f}% [{fpr_ci[0]*100:.2f}%, {fpr_ci[1]*100:.2f}%]",
                "Precision": f"{precision*100:.2f}%",
                "False Withdrawals / 1000": round(fw_1000, 1),
                "Sc10": round(sc10, 1),
                "Sc50": round(sc50, 1),
                "Sc100": round(sc100, 1),
                "Provenance": "DEVELOPMENT"
            })
'''

old = '''
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
'''

content = content.replace(old.strip(), replacement.strip())
with open('agnipariksha/evaluation/evaluator.py', 'w') as f:
    f.write(content)
