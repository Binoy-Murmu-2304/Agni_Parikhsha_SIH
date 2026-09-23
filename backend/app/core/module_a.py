import numpy as np
import pandas as pd
from scipy import stats
from sklearn.covariance import MinCovDet
from sklearn.ensemble import IsolationForest
from pyod.models.lof import LOF

def robust_univariate_baseline(
    series: pd.Series, 
    datasheet_limit: float = None,
    prior_median: float = None,
    prior_spread: float = None,
    small_lot_threshold: int = 30,
    k: int = 15
) -> pd.DataFrame:
    """
    Computes robust median, spread, and z-scores for a series of values.
    Applies small-lot shrinkage if priors are provided and n < threshold.
    """
    n = len(series.dropna())
    if n == 0:
        return pd.DataFrame({"z_score": [], "flagged": []}, index=series.index)
        
    median = series.median()
    iqr = series.quantile(0.75) - series.quantile(0.25)
    spread = iqr / 1.35
    
    if spread == 0:
        # Fallback if IQR is 0
        spread = series.std()
        if spread == 0 or pd.isna(spread):
            spread = 1e-6
            
    # Small-lot shrinkage
    if n < small_lot_threshold and prior_median is not None and prior_spread is not None:
        w = n / (n + k)
        median = w * median + (1 - w) * prior_median
        spread = w * spread + (1 - w) * prior_spread
        
    z_scores = (series - median) / spread
    
    # Calculate limits
    upper_limit = median + 6 * spread
    lower_limit = median - 6 * spread
    
    if datasheet_limit is not None:
        # Assuming datasheet limit is an upper bound. 
        upper_limit = min(upper_limit, datasheet_limit)
        
    flagged = (series > upper_limit) | (series < lower_limit)
    
    return pd.DataFrame({
        "value": series,
        "robust_median": median,
        "robust_spread": spread,
        "z_score": z_scores,
        "flagged_univariate": flagged
    }, index=series.index)

def multivariate_mcd_check(
    df: pd.DataFrame, 
    features: list
) -> pd.DataFrame:
    """
    Computes Mahalanobis distance using Minimum Covariance Determinant.
    Returns distances and feature attributions.
    """
    # Drop rows with NaNs in features
    valid_mask = df[features].notna().all(axis=1)
    X = df.loc[valid_mask, features].values
    
    if len(X) < len(features) + 1:
        # Not enough data for MCD
        return pd.DataFrame(index=df.index)
        
    # Fit MCD
    try:
        # MCD requires n_samples > n_features.
        # For very small lots, standard covariance or pseudo-inverse might be needed,
        # but the prompt specifies MCD.
        mcd = MinCovDet(random_state=42).fit(X)
    except ValueError:
        # Fallback to standard covariance if MCD fails (e.g. singular)
        cov = np.cov(X.T)
        mean = np.mean(X, axis=0)
        from sklearn.covariance import EmpiricalCovariance
        mcd = EmpiricalCovariance().fit(X)
        
    dist = mcd.mahalanobis(X)
    
    # Attribution via Whitening
    # Mahalanobis squared = (x-mu)^T @ Cov^-1 @ (x-mu)
    # Let L be Cholesky of Cov^-1. Whitened x_w = L^T @ (x-mu)
    # Then Mahalanobis squared = sum(x_w^2)
    try:
        inv_cov = mcd.precision_
        L = np.linalg.cholesky(inv_cov)
        X_centered = X - mcd.location_
        X_whitened = X_centered @ L
        attribution = X_whitened ** 2
    except np.linalg.LinAlgError:
        # If precision matrix is not positive definite
        attribution = np.zeros_like(X)
        
    res_df = pd.DataFrame(index=df[valid_mask].index)
    res_df["mahalanobis_dist"] = dist
    
    for i, col in enumerate(features):
        res_df[f"attr_{col}"] = attribution[:, i]
        
    return res_df

def density_ensemble_check(
    df: pd.DataFrame,
    features: list
) -> pd.DataFrame:
    """
    Runs Isolation Forest and LOF, combines by rank-max.
    """
    valid_mask = df[features].notna().all(axis=1)
    X = df.loc[valid_mask, features].values
    
    if len(X) < 5:
        return pd.DataFrame(index=df.index)
        
    # Scale features robustly for distance-based LOF
    from sklearn.preprocessing import RobustScaler
    X_scaled = RobustScaler().fit_transform(X)
    
    # Isolation Forest
    iso = IsolationForest(random_state=42, contamination=0.1)
    iso.fit(X_scaled)
    # decision_function returns >0 for normal, <0 for anomalies. Invert for anomaly score.
    iso_scores = -iso.decision_function(X_scaled)
    
    # LOF
    lof = LOF(n_neighbors=min(20, len(X)-1), contamination=0.1)
    lof.fit(X_scaled)
    lof_scores = lof.decision_scores_
    
    # Instead of uniform ranks which punishes healthy parts, 
    # we convert the ensemble scores to a pseudo-probability using absolute thresholds.
    # For Isolation Forest: decision_function < 0 is anomaly. We inverted it, so iso_score > 0 is anomaly.
    # For LOF: decision_scores_ > 1.5 is typically an anomaly.
    
    # Scale IF score (typically ranges up to 0.5)
    a_iso = np.clip(iso_scores * 5.0, 0, 1)
    
    # Scale LOF score (penalize anything above 1.5)
    a_lof = np.clip((lof_scores - 1.5), 0, 1)
    
    max_a = np.maximum(a_iso, a_lof)
    
    res_df = pd.DataFrame(index=df[valid_mask].index)
    res_df["if_score"] = iso_scores
    res_df["lof_score"] = lof_scores
    res_df["anomaly_score"] = max_a

    
    return res_df

def conformal_p_value(
    scores: pd.Series,
    calibration_scores: np.ndarray
) -> pd.Series:
    """
    Converts raw anomaly scores to calibrated p-values using a calibration set.
    """
    n_cal = len(calibration_scores)
    if n_cal == 0:
        # Fallback if no calibration data: uniform p-values or rank-based
        return 1.0 - stats.rankdata(scores) / len(scores)
        
    p_values = []
    # Sort calibration scores for faster search
    cal_sorted = np.sort(calibration_scores)
    
    for score in scores:
        # count how many calibration scores are >= this score
        count_greater_eq = n_cal - np.searchsorted(cal_sorted, score)
        p = (1 + count_greater_eq) / (n_cal + 1)
        p_values.append(p)
        
    return pd.Series(p_values, index=scores.index)

def run_module_a(
    df: pd.DataFrame, 
    timepoints: list = None,
    datasheet_limits: dict = None
):
    """
    Runs the full Module A pipeline for a given lot across timepoints.
    Expects df to be long-format: part_id, parameter_name, timepoint_hours, value.
    """
    results = []
    # In a real system, we'd loop over lots if df contains multiple.
    # Assuming df is one lot here or grouped beforehand.
    
    if timepoints is None:
        timepoints = df['timepoint_hours'].unique()
        
    for t in timepoints:
        t_df = df[df['timepoint_hours'] == t].copy()
        if t_df.empty:
            continue
            
        # Pivot to wide for multivariate
        wide_df = t_df.pivot(index='part_id', columns='parameter_name', values='value')
        features = list(wide_df.columns)
        
        # Univariate
        uni_res_list = []
        for param in features:
            limit = datasheet_limits.get(param) if datasheet_limits else None
            series = wide_df[param]
            u_res = robust_univariate_baseline(series, datasheet_limit=limit)
            u_res['parameter_name'] = param
            u_res['timepoint_hours'] = t
            u_res['part_id'] = u_res.index
            uni_res_list.append(u_res)
            
        # Multivariate
        mcd_res = multivariate_mcd_check(wide_df, features)
        
        # Density Ensemble
        ens_res = density_ensemble_check(wide_df, features)
        
        # Combine
        t_res = wide_df.copy()
        t_res['timepoint_hours'] = t
        
        if not mcd_res.empty:
            t_res = t_res.join(mcd_res)
        if not ens_res.empty:
            t_res = t_res.join(ens_res)
            
        results.append(t_res.reset_index())
        
    if not results:
        return pd.DataFrame()
        
    return pd.concat(results, ignore_index=True)
