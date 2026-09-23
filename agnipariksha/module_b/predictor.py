import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from typing import Dict, Tuple, Optional
from ..config import FAMILY_SPECS, SAFETY_SLOPE_K_REL, SAFETY_SLOPE_K_ROB

class DriftPredictor:
    """
    Module B: Drift Predictor + Conformal + Safety Slope
    """
    
    def __init__(self):
        # One model per family
        self.models: Dict[str, HistGradientBoostingRegressor] = {}
        # Conformal q_alpha per family for 90% and 95% coverage targets
        self.q_alphas_90: Dict[str, float] = {}
        self.q_alphas_95: Dict[str, float] = {}

    def extract_features(self, df: pd.DataFrame, current_hour: int = 24) -> pd.DataFrame:
        """
        Extracts strictly <= current_hour features.
        """
        # The caller may pass a dataframe with future columns, but we will ONLY extract 
        # features up to current_hour.
        features = pd.DataFrame(index=df.index)
        
        if current_hour >= 24:
            features['val_0h'] = df['value_0h']
            features['val_24h'] = df['value_24h']
            features['slope_24h'] = (df['value_24h'] - df['value_0h']) / 24.0
            
            # --- PHYSICS MAPPING FEATURES (Phase 4.2) ---
            # Electromigration (current-density x time): uses value_24h as proxy for current
            features['EM_stress'] = df['value_24h'] * current_hour
            
            # SRH traps (saturating kinetics f(t) = A(1 - exp(-t/tau)))
            # Using value_24h as a proxy for the saturation magnitude A
            features['SRH_kinetics'] = df['value_24h'] * (1.0 - np.exp(-current_hour / 50.0))
            
            # Viscoelastic creep (log-time feature)
            features['creep_log_time'] = features['slope_24h'] * np.log1p(current_hour)
            
            # Arrhenius acceleration exp(-Ea/kT) at 125C (398.15K) with Ea=0.7eV
            arrhenius_factor = np.exp(-0.7 / (8.617e-5 * 398.15))
            features['arrhenius_drift'] = features['slope_24h'] * arrhenius_factor
            
        if current_hour >= 96:
            features['val_96h'] = df.get('value_96h', np.nan)
            if 'value_96h' in df.columns:
                features['slope_96h'] = (df['value_96h'] - df['value_24h']) / (96.0 - 24.0)
                
        return features

    def fit(self, df_train: pd.DataFrame, df_cal: pd.DataFrame):
        """
        Fits models on TRAIN, computes conformal q_alpha on CALIBRATION.
        """
        for family in df_train['family'].unique():
            df_f_train = df_train[df_train['family'] == family]
            
            df_features = df_f_train.drop(columns=['value_168h']) if 'value_168h' in df_f_train.columns else df_f_train
            X_train = self.extract_features(df_features, current_hour=24)
            y_train = df_f_train['value_168h']
            
            # hyperparameters fixed (D4) - just basic defaults for HGB
            model = HistGradientBoostingRegressor(random_state=42)
            model.fit(X_train, y_train)
            self.models[family] = model
            
            # Conformal calibration
            df_f_cal = df_cal[df_cal['family'] == family]
            if len(df_f_cal) > 0:
                df_cal_features = df_f_cal.drop(columns=['value_168h']) if 'value_168h' in df_f_cal.columns else df_f_cal
                X_cal = self.extract_features(df_cal_features, current_hour=24)
                y_cal = df_f_cal['value_168h']
                preds_cal = model.predict(X_cal)
                residuals = np.abs(y_cal - preds_cal)
                
                n_cal = len(residuals)
                # target alpha = 0.10 (90% coverage)
                q_90_idx = int(np.ceil((n_cal + 1) * 0.90))
                # target alpha = 0.05 (95% coverage)
                q_95_idx = int(np.ceil((n_cal + 1) * 0.95))
                
                # cap indices to max available
                q_90_idx = min(q_90_idx, n_cal)
                q_95_idx = min(q_95_idx, n_cal)
                
                sorted_residuals = np.sort(residuals.values)
                self.q_alphas_90[family] = sorted_residuals[q_90_idx - 1]
                self.q_alphas_95[family] = sorted_residuals[q_95_idx - 1]
            else:
                self.q_alphas_90[family] = 0.0
                self.q_alphas_95[family] = 0.0

    def predict_with_conformal(self, df: pd.DataFrame, family: str) -> pd.DataFrame:
        """
        Predicts 168h value and conformal intervals.
        """
        res = pd.DataFrame(index=df.index)
        if family not in self.models:
            res['pred_168h'] = np.nan
            res['conformal_radius_90'] = np.nan
            res['conformal_radius_95'] = np.nan
            return res
            
        X = self.extract_features(df, current_hour=24)
        preds = self.models[family].predict(X)
        
        res['pred_168h'] = preds
        res['conformal_radius_90'] = self.q_alphas_90.get(family, 0.0)
        res['conformal_radius_95'] = self.q_alphas_95.get(family, 0.0)
        
        return res

    def compute_safety_slope(self, df_lot: pd.DataFrame, current_hour: int = 24) -> pd.DataFrame:
        """
        Safety Slope Logic: 
        min(headroom_bound, relative_bound)
        """
        df = df_lot.copy()
        family = df['family'].iloc[0]
        
        if f'value_{current_hour}h' not in df.columns or df[f'value_{current_hour}h'].isna().all():
            df['module_b_verdict'] = 'FULL_BURN_IN'
            df['module_b_reason'] = f'Missing {current_hour}h checkpoint data'
            return df

        spec_max = FAMILY_SPECS[family]['spec_max']
        
        remaining_hours = 168.0 - current_hour
        
        # Calculate raw slope
        df['measured_slope'] = (df[f'value_{current_hour}h'] - df['value_0h']) / current_hour
        
        # Headroom bound: (SpecMax - current_value) / remaining_hours
        df['headroom_bound'] = (spec_max - df[f'value_{current_hour}h']) / remaining_hours
        
        # Relative bound: k_rel * SpecMax / 168h
        df['relative_bound'] = (SAFETY_SLOPE_K_REL * spec_max) / 168.0
        
        # BINDING BOUND: MUST BE MIN()
        df['allowed_slope'] = df[['headroom_bound', 'relative_bound']].min(axis=1)
        
        # Lot stats bound
        median_slope = df['measured_slope'].median()
        mad_slope = (df['measured_slope'] - median_slope).abs().median()
        if mad_slope < 1e-6:
            mad_slope = max(abs(median_slope) * 0.01, 1e-4)
            
        df['lot_stat_bound'] = median_slope + SAFETY_SLOPE_K_ROB * mad_slope
        
        # Predict future slope using our model
        preds = self.predict_with_conformal(df, family)
        df['pred_168h'] = preds['pred_168h']
        df['pred_slope'] = (df['pred_168h'] - df[f'value_{current_hour}h']) / remaining_hours
        
        def evaluate_safety(row):
            max_slope = max(row['measured_slope'], row['pred_slope'])
            if max_slope > row['allowed_slope']:
                return 'RED_SAFETY_SLOPE'
            if max_slope > row['lot_stat_bound']:
                return 'YELLOW_STAT_SLOPE'
            return 'GREEN'
            
        df['module_b_verdict'] = df.apply(evaluate_safety, axis=1)
        return df
