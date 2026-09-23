import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel, DotProduct

class PhysicsGBDTDriftPredictor:
    def __init__(self, n_power=0.5):
        self.n_power = n_power
        self.p50_model = lgb.LGBMRegressor(objective='quantile', alpha=0.5, random_state=42)
        self.p95_model = lgb.LGBMRegressor(objective='quantile', alpha=0.95, random_state=42)
        self.is_fitted = False
        
    def _extract_physics_features(self, df_part):
        """ Extract b and V0 based on first two timepoints """
        df_sorted = df_part.sort_values('timepoint_hours')
        if len(df_sorted) < 2:
            return None
            
        t0, t1 = df_sorted['timepoint_hours'].iloc[0], df_sorted['timepoint_hours'].iloc[1]
        v0, v1 = df_sorted['value'].iloc[0], df_sorted['value'].iloc[1]
        
        # V(t) = V0 + b * t^n -> b = (V(t) - V0) / t^n
        b = (v1 - v0) / (t1**self.n_power) if t1 > 0 else 0
        return {"v0": v0, "b": b, "t0": t0, "t1": t1, "v1": v1}
        
    def fit(self, historical_df: pd.DataFrame, target_time: float):
        """
        historical_df: long format, requires part_id, timepoint_hours, value
        """
        features = []
        targets = []
        
        for part_id, group in historical_df.groupby('part_id'):
            phys = self._extract_physics_features(group)
            if phys is None:
                continue
                
            # Find target value
            target_row = group[group['timepoint_hours'] == target_time]
            if target_row.empty:
                continue
                
            y = target_row['value'].values[0]
            
            # Predict using pure physics
            phys_pred = phys['v0'] + phys['b'] * (target_time ** self.n_power)
            residual = y - phys_pred
            
            features.append([phys['v0'], phys['v1'], phys['b']])
            targets.append(residual)
            
        if not features:
            return
            
        X = np.array(features)
        y = np.array(targets)
        
        self.p50_model.fit(X, y)
        self.p95_model.fit(X, y)
        self.is_fitted = True
        
    def predict(self, current_df: pd.DataFrame, target_time: float):
        """ Predict for a new part """
        res = []
        for part_id, group in current_df.groupby('part_id'):
            phys = self._extract_physics_features(group)
            if phys is None:
                continue
                
            phys_pred = phys['v0'] + phys['b'] * (target_time ** self.n_power)
            
            if self.is_fitted:
                X = np.array([[phys['v0'], phys['v1'], phys['b']]])
                res_p50 = self.p50_model.predict(X)[0]
                res_p95 = self.p95_model.predict(X)[0]
            else:
                res_p50, res_p95 = 0, 0
                
            p50 = phys_pred + res_p50
            p95 = phys_pred + res_p95
            
            # Compute implied slope to target
            last_t = group['timepoint_hours'].max()
            last_v = group[group['timepoint_hours'] == last_t]['value'].values[0]
            
            implied_slope = (p95 - last_v) / (target_time - last_t) if target_time > last_t else 0
            
            res.append({
                "part_id": part_id,
                "predicted_p50": p50,
                "predicted_p95": p95,
                "implied_slope": implied_slope
            })
            
        return pd.DataFrame(res)

class GPDriftPredictor:
    def __init__(self):
        # Kernel: Linear + RBF for trend + local variation, plus noise
        self.kernel = DotProduct() + RBF(length_scale=10.0) + WhiteKernel(noise_level=1)
        self.model = GaussianProcessRegressor(kernel=self.kernel, n_restarts_optimizer=5, random_state=42)
        
    def predict(self, current_df: pd.DataFrame, target_time: float):
        res = []
        for part_id, group in current_df.groupby('part_id'):
            group = group.sort_values('timepoint_hours')
            X = group[['timepoint_hours']].values
            y = group['value'].values
            
            if len(X) < 2:
                continue
                
            # Fit GP on this specific part's trajectory (zero-shot fallback)
            try:
                # Scale X for better GP fitting
                X_scaled = X / target_time 
                t_target_scaled = np.array([[target_time / target_time]])
                
                gp = GaussianProcessRegressor(kernel=self.kernel, n_restarts_optimizer=0, normalize_y=True)
                gp.fit(X_scaled, y)
                
                mean, std = gp.predict(t_target_scaled, return_std=True)
                mean = mean[0]
                std = std[0]
                
                p50 = mean
                p95 = mean + 1.645 * std
                
                last_t = X[-1][0]
                last_v = y[-1]
                implied_slope = (p95 - last_v) / (target_time - last_t) if target_time > last_t else 0
                
                res.append({
                    "part_id": part_id,
                    "predicted_p50": p50,
                    "predicted_p95": p95,
                    "implied_slope": implied_slope
                })
            except Exception as e:
                pass
                
        return pd.DataFrame(res)

def run_module_b(
    df: pd.DataFrame, 
    historical_df: pd.DataFrame = None,
    backend: str = 'gbdt',
    target_time: float = 168.0,
    safety_slope: float = 0.5
):
    """
    Runs drift prediction for parts in df.
    """
    if backend == 'gbdt':
        predictor = PhysicsGBDTDriftPredictor()
        if historical_df is not None and not historical_df.empty:
            predictor.fit(historical_df, target_time)
        res_df = predictor.predict(df, target_time)
    else:
        predictor = GPDriftPredictor()
        res_df = predictor.predict(df, target_time)
        
    if res_df.empty:
        return pd.DataFrame()
        
    res_df['safety_slope'] = safety_slope
    res_df['drift_flagged'] = res_df['implied_slope'] > safety_slope
    
    return res_df
