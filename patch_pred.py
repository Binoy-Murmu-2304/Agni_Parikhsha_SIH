import os
with open('agnipariksha/module_b/predictor.py', 'r') as f:
    c = f.read()
c = c.replace('''        df['pred_168h'] = preds['pred_168h']
        df['pred_slope'] = (df['pred_168h'] - df[f'value_{current_hour}h']) / remaining_hours''', '''        df['pred_168h'] = preds['pred_168h']
        df['conformal_radius_90'] = preds['conformal_radius_90']
        df['conformal_radius_95'] = preds['conformal_radius_95']
        df['pred_slope'] = (df['pred_168h'] - df[f'value_{current_hour}h']) / remaining_hours''')
with open('agnipariksha/module_b/predictor.py', 'w') as f:
    f.write(c)
