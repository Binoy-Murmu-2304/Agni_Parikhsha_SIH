import os

with open('agnipariksha/evaluation/evaluator.py', 'r') as f:
    content = f.read()

replacement = '''
            tp = len(df_res[(df_res['is_defective'] == 1) & (df_res['final_flag'] == 1)])
            fn = len(df_res[(df_res['is_defective'] == 1) & (df_res['final_flag'] == 0)])
            fp = len(df_res[(df_res['is_defective'] == 0) & (df_res['final_flag'] == 1)])
            tn = len(df_res[(df_res['is_defective'] == 0) & (df_res['final_flag'] == 0)])
            
            escape_fn = len(df_res[(df_res['is_defective'] == 1) & (df_res['disposition'] == 'GREEN')])
'''

old = '''
            tp = len(df_res[(df_res['is_defective'] == 1) & (df_res['final_flag'] == 1)])
            fn = len(df_res[(df_res['is_defective'] == 1) & (df_res['final_flag'] == 0)])
            fp = len(df_res[(df_res['is_defective'] == 0) & (df_res['final_flag'] == 1)])
            tn = len(df_res[(df_res['is_defective'] == 0) & (df_res['final_flag'] == 0)])
'''

content = content.replace(old.strip(), replacement.strip())

replacement2 = '''
            sc10 = self.calculate_score(fp, fn, n_total, w_fn=10)
            sc50 = self.calculate_score(fp, fn, n_total, w_fn=50)
            sc100 = self.calculate_score(fp, fn, n_total, w_fn=100)
            sc50_escape = self.calculate_score(fp, escape_fn, n_total, w_fn=50)
            
            results.append({
                "Prevalence": f"{rate*100:.1f}%",
                "N": n_total,
                "n_def": n_def_actual,
                "TP": tp,
                "FN": fn,
                "Escape-FN": escape_fn,
                "FP": fp,
                "Recall (bound)": f"{recall*100:.2f}% [{rec_ci[0]*100:.2f}%, {rec_ci[1]*100:.2f}%]",
                "FPR (bound)": f"{fpr*100:.2f}% [{fpr_ci[0]*100:.2f}%, {fpr_ci[1]*100:.2f}%]",
                "Precision": f"{precision*100:.2f}%",
                "False Withdrawals / 1000": round(fw_1000, 1),
                "Sc10": round(sc10, 1),
                "Sc50": round(sc50, 1),
                "Sc50 (Escape)": round(sc50_escape, 1),
                "Sc100": round(sc100, 1),
                "Provenance": "DEVELOPMENT"
            })
'''

old2 = '''
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

content = content.replace(old2.strip(), replacement2.strip())
with open('agnipariksha/evaluation/evaluator.py', 'w') as f:
    f.write(content)
