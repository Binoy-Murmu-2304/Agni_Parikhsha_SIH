import pandas as pd
import numpy as np
import re
from typing import Dict, List, Tuple, Any

def normalize_dataset(
    df: pd.DataFrame, 
    column_mapping: Dict[str, str] = None
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Normalizes a wide-format dataset into the canonical long-format table.
    If column_mapping is None, attempts to auto-detect columns.
    Returns:
        canonical_df (pd.DataFrame): The normalized data.
        warnings (List[str]): Validation warnings (e.g. small lots).
    """
    warnings = []
    
    if column_mapping is None:
        column_mapping = auto_detect_columns(df.columns)
        
    # Validate mapping
    if not column_mapping.get("part_id"):
        raise ValueError("part_id column could not be determined.")
    if not column_mapping.get("lot_id"):
        raise ValueError("lot_id column could not be determined.")
    if not column_mapping.get("timepoints") or len(column_mapping["timepoints"]) < 2:
        raise ValueError("At least 2 timepoint columns are required.")
        
    part_col = column_mapping["part_id"]
    lot_col = column_mapping["lot_id"]
    wafer_col = column_mapping.get("wafer_id")
    param_col = column_mapping.get("parameter_name")
    timepoints = column_mapping["timepoints"] # dict of {original_col: numeric_hours}
    
    # Check duplicate part IDs
    if df.duplicated(subset=[part_col]).any():
        warnings.append("Duplicate part IDs found. Duplicates will be dropped or averaged (currently keeping first).")
        df = df.drop_duplicates(subset=[part_col])
        
    # Check lot sizes
    lot_sizes = df.groupby(lot_col).size()
    small_lots = lot_sizes[lot_sizes < 5].index.tolist()
    if small_lots:
        warnings.append(f"Lots with < 5 parts found: {small_lots}. Statistics may be unreliable.")

    # Melt to long format
    id_vars = [part_col, lot_col]
    if wafer_col and wafer_col in df.columns:
        id_vars.append(wafer_col)
    if param_col and param_col in df.columns:
        id_vars.append(param_col)
        
    value_vars = list(timepoints.keys())
    
    long_df = pd.melt(
        df, 
        id_vars=id_vars,
        value_vars=value_vars,
        var_name="timepoint_label",
        value_name="value"
    )
    
    # Standardize column names
    rename_map = {
        part_col: "part_id",
        lot_col: "lot_id"
    }
    if wafer_col:
        rename_map[wafer_col] = "wafer_id"
        
    long_df.rename(columns=rename_map, inplace=True)
    
    if param_col:
        long_df.rename(columns={param_col: "parameter_name"}, inplace=True)
    else:
        # Default parameter name if not provided
        long_df["parameter_name"] = "Unknown_Parameter"
        
    # Ensure wafer_id exists
    if "wafer_id" not in long_df.columns:
        long_df["wafer_id"] = None
        
    # Map timepoint labels to numeric hours
    long_df["timepoint_hours"] = long_df["timepoint_label"].map(timepoints)
    
    # Convert value to numeric, coercing errors to NaN
    long_df["value"] = pd.to_numeric(long_df["value"], errors='coerce')
    
    # Drop rows where value is NaN
    nan_count = long_df["value"].isna().sum()
    if nan_count > 0:
        warnings.append(f"Dropped {nan_count} readings with non-numeric or missing values.")
        long_df = long_df.dropna(subset=["value"])
        
    # Reorder columns to canonical format
    canonical_columns = [
        "part_id", "lot_id", "wafer_id", "parameter_name", 
        "timepoint_label", "timepoint_hours", "value"
    ]
    long_df = long_df[canonical_columns]
    
    return long_df, warnings

def auto_detect_columns(columns: List[str]) -> Dict[str, Any]:
    """
    Heuristics to detect column roles from names.
    """
    mapping = {
        "part_id": None,
        "lot_id": None,
        "wafer_id": None,
        "parameter_name": None,
        "timepoints": {}
    }
    
    time_pattern = re.compile(r'^t?(\d+(?:\.\d+)?)\s*(?:h|hr|hours?)?$', re.IGNORECASE)
    
    for col in columns:
        col_lower = col.lower()
        
        if not mapping["part_id"] and ("part" in col_lower or "id" == col_lower or "device" in col_lower):
            mapping["part_id"] = col
        elif not mapping["lot_id"] and "lot" in col_lower:
            mapping["lot_id"] = col
        elif not mapping["wafer_id"] and "wafer" in col_lower:
            mapping["wafer_id"] = col
        elif not mapping["parameter_name"] and ("param" in col_lower or "test" in col_lower):
            mapping["parameter_name"] = col
        else:
            # Check if it's a timepoint
            match = time_pattern.match(col)
            if match:
                hours = float(match.group(1))
                mapping["timepoints"][col] = hours
                
    return mapping
