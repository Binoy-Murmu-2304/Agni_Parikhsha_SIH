import numpy as np
import pandas as pd

def calculate_cri(
    mod_a_df: pd.DataFrame, 
    mod_b_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Combines Module A and Module B outputs to calculate CRI.
    """
    # Assuming mod_a_df has 'part_id', 'anomaly_score', 'flagged_univariate', 'mahalanobis_dist'
    # Assuming mod_b_df has 'part_id', 'implied_slope', 'safety_slope'
    
    # We will compute a unified 'a' from module A. 
    # If conformal p_value is missing, use ensemble rank/anomaly_score
    if 'conformal_p' in mod_a_df.columns:
        a = 1.0 - mod_a_df['conformal_p']
    elif 'anomaly_score' in mod_a_df.columns:
        a = mod_a_df['anomaly_score']
    else:
        a = pd.Series(0, index=mod_a_df.index)
        
    a = np.clip(a, 0, 1)
    
    # Merge on part_id
    # We might have multiple timepoints, usually CRI is based on latest available.
    # Let's assume mod_a_df is grouped/latest.
    
    # Group by part_id and get max 'a' if multiple params
    a_df = pd.DataFrame({'part_id': mod_a_df['part_id'], 'a_score': a})
    a_max = a_df.groupby('part_id')['a_score'].max().reset_index()
    
    df_merged = a_max
    
    if mod_b_df is not None and not mod_b_df.empty:
        df_merged = pd.merge(df_merged, mod_b_df[['part_id', 'implied_slope', 'safety_slope']], on='part_id', how='left')
        
        # d = clip((predicted_slope - safety_slope) / safety_slope, 0, 1)
        d_val = (df_merged['implied_slope'] - df_merged['safety_slope']) / df_merged['safety_slope'].replace(0, 1e-6)
        df_merged['d_score'] = np.clip(d_val.fillna(0), 0, 1)
    else:
        df_merged['d_score'] = 0.0
        
    df_merged['cri'] = 100.0 * (1.0 - np.maximum(df_merged['a_score'], df_merged['d_score']))
    
    return df_merged

def assign_verdict(cri_series: pd.Series, reject_thresh: float = 30.0, review_thresh: float = 80.0) -> pd.Series:
    """
    Assigns ACCEPT / REVIEW / REJECT verdicts.
    """
    def get_tier(cri):
        if pd.isna(cri):
            return "REVIEW"
        if cri < reject_thresh:
            return "REJECT"
        elif cri < review_thresh:
            return "REVIEW"
        else:
            return "ACCEPT"
            
    return cri_series.apply(get_tier)

def run_module_c(
    mod_a_df: pd.DataFrame, 
    mod_b_df: pd.DataFrame,
    reject_thresh: float = 30.0,
    review_thresh: float = 80.0
) -> pd.DataFrame:
    
    fusion_df = calculate_cri(mod_a_df, mod_b_df)
    fusion_df['verdict'] = assign_verdict(fusion_df['cri'], reject_thresh, review_thresh)
    
    return fusion_df
