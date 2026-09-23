"""
Module A: Dynamic Outlier Detection (Lot-adaptive)
"""
import numpy as np
import pandas as pd
from scipy.spatial.distance import mahalanobis
from ..config import MODULE_A_MIN_LOT_SIZE

class DynamicOutlierDetector:
    """
    Detects anomalies dynamically based on the lot's own population (D1, D4).
    """
    
    def __init__(self, z_yellow: float = 3.5, z_red: float = 5.0, maha_threshold: float = 4.0):
        # Thresholds derived or documented (D4)
        self.z_yellow = z_yellow
        self.z_red = z_red
        self.maha_threshold = maha_threshold

    def compute_robust_stats(self, series: pd.Series) -> tuple:
        """
        Computes median and MAD.
        If MAD ≈ 0, sets a documented floor.
        """
        median = series.median()
        # MAD = median(|x_i - median(X)|)
        mad = (series - median).abs().median()
        
        # Guard against MAD=0 (perfectly identical readings)
        if mad < 1e-6:
            # Documented floor: 1% of median, or tiny constant if median is 0
            mad = max(abs(median) * 0.01, 1e-4)
            
        return median, mad

    def compute_z_score(self, val: float, median: float, mad: float) -> float:
        """
        Robust Z-score: Z = |x - median| / (1.4826 * MAD)
        """
        return abs(val - median) / (1.4826 * mad)

    def detect_univariate(self, df_lot: pd.DataFrame, param_col: str) -> pd.DataFrame:
        """
        Detects univariate outliers in a lot for a specific parameter column (e.g., 'value_24h').
        """
        df = df_lot.copy()
        n_components = len(df)
        
        if n_components < MODULE_A_MIN_LOT_SIZE:
            # Guard for tiny lots: escalate to full burn-in
            df['module_a_z_score'] = np.nan
            df['module_a_verdict'] = 'FULL_BURN_IN'
            df['module_a_reason'] = f'Lot size {n_components} < {MODULE_A_MIN_LOT_SIZE}. Insufficient statistics.'
            return df
            
        median, mad = self.compute_robust_stats(df[param_col])
        
        df['module_a_z_score'] = df[param_col].apply(lambda x: self.compute_z_score(x, median, mad))
        
        # Cascade
        def get_verdict(z):
            if z > self.z_red:
                return 'RED'
            elif z > self.z_yellow:
                return 'YELLOW'
            return 'GREEN'
            
        df['module_a_verdict'] = df['module_a_z_score'].apply(get_verdict)
        df['module_a_reason'] = df.apply(
            lambda row: f"Z-score {row['module_a_z_score']:.2f} > {self.z_red} (RED)" if row['module_a_verdict'] == 'RED' else
                        f"Z-score {row['module_a_z_score']:.2f} > {self.z_yellow} (YELLOW)" if row['module_a_verdict'] == 'YELLOW' else "Normal",
            axis=1
        )
        return df

    def detect_multivariate(self, df_lot: pd.DataFrame, feature_cols: list) -> pd.DataFrame:
        """
        Multi-parametric outlier layer using Mahalanobis distance.
        Uses shrinkage covariance if n is small.
        """
        df = df_lot.copy()
        n_components = len(df)
        
        if n_components < MODULE_A_MIN_LOT_SIZE:
            df['module_a_maha_dist'] = np.nan
            df['module_a_maha_verdict'] = 'FULL_BURN_IN'
            return df

        X = df[feature_cols].values
        means = np.mean(X, axis=0)
        
        # Covariance with Ledoit-Wolf shrinkage to handle small lots
        from sklearn.covariance import LedoitWolf
        lw = LedoitWolf()
        try:
            lw.fit(X)
            inv_cov = lw.precision_
        except Exception:
            # Fallback to diagonal variance if perfectly collinear or zero var
            inv_cov = np.diag(1.0 / (np.var(X, axis=0) + 1e-6))
            
        maha_dists = [mahalanobis(x, means, inv_cov) for x in X]
        df['module_a_maha_dist'] = maha_dists
        
        df['module_a_maha_verdict'] = np.where(df['module_a_maha_dist'] > self.maha_threshold, 'RED', 'GREEN')
        return df
