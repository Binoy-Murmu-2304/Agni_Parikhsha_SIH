import pandas as pd
import numpy as np
import argparse
from typing import List, Dict

def generate_synthetic_lot(
    lot_id: str,
    part_type: str = "UnknownPart",
    lot_size: int = 100,
    checkpoints: List[float] = [0, 24, 96, 168],
    parameters: List[Dict] = [{"name": "Iddq_uA", "baseline": 10.0, "spread": 0.5}],
    defect_rate: float = 0.03,
    archetypes: List[str] = ["elevated_drift", "shape_change", "knee_defect"],
    random_seed: int = None
) -> pd.DataFrame:
    """
    Generate synthetic burn-in data for a single lot.
    """
    if random_seed is not None:
        np.random.seed(random_seed)

    # Base physics model: V(t) = V0 + b * t^n
    n_healthy = 0.5 # square root over time typical for diffusion

    parts = []
    num_defects = int(np.ceil(lot_size * defect_rate))
    defect_indices = np.random.choice(lot_size, num_defects, replace=False)
    
    # Pre-determine defect assignments per part
    part_defects = {}
    for idx in defect_indices:
        arch = np.random.choice(archetypes) if archetypes else "elevated_drift"
        part_defects[idx] = arch

    for i in range(lot_size):
        part_id = f"{lot_id}_P{i+1:04d}"
        is_defective = i in part_defects
        defect_type = part_defects.get(i, "None")
        
        # Decide which parameter will carry the defect (can be one or multiple)
        # For simplicity, assign defect to the first parameter, or random parameter.
        defect_param_idx = np.random.choice(len(parameters)) if is_defective else -1
        
        for p_idx, param in enumerate(parameters):
            param_name = param["name"]
            v0_mu = param["baseline"]
            v0_sigma = param["spread"]
            
            b_mu, b_sigma = v0_mu * 0.002, v0_mu * 0.0005 # scale drift by baseline
            
            v0 = np.random.normal(v0_mu, v0_sigma)
            b = np.random.normal(b_mu, b_sigma)
            n = n_healthy
            
            knee_time = None
            
            is_param_defective = is_defective and p_idx == defect_param_idx
            
            if is_param_defective:
                if defect_type == "elevated_drift":
                    b = np.random.normal(b_mu * 5, b_sigma * 2)
                elif defect_type == "shape_change":
                    n = 1.2 # linear or super-linear
                elif defect_type == "knee_defect":
                    knee_time = np.random.choice(checkpoints[1:-1]) if len(checkpoints) > 2 else checkpoints[-1]/2
                    
            part_data = {
                "PartID": part_id,
                "LotID": lot_id,
                "PartType": part_type,
                "Parameter": param_name,
                "IsDefective_GT": is_defective,
                "DefectType_GT": defect_type
            }
            
            for t in checkpoints:
                # Calculate value
                if t == 0:
                    val = v0
                else:
                    if is_param_defective and defect_type == "knee_defect" and t > knee_time:
                        # Accelerate drift after knee
                        val = v0 + b * (knee_time**n) + (b * 10) * ((t - knee_time)**n)
                    else:
                        val = v0 + b * (t**n)
                
                # Add measurement noise
                noise = np.random.normal(0, v0_mu * 0.005)
                part_data[f"{t}h"] = round(val + noise, 4)
                
            parts.append(part_data)
        
    return pd.DataFrame(parts)

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic ESS dataset")
    parser.add_argument("--lots", type=int, default=5, help="Number of lots")
    parser.add_argument("--lot-size", type=int, default=50, help="Parts per lot")
    parser.add_argument("--out", type=str, default="synthetic_burnin_data.csv", help="Output file")
    
    args = parser.parse_args()
    
    all_data = []
    for lot_idx in range(args.lots):
        lot_id = f"LOT_2024_{lot_idx+1:03d}"
        df = generate_synthetic_lot(lot_id=lot_id, lot_size=args.lot_size)
        all_data.append(df)
        
    final_df = pd.concat(all_data, ignore_index=True)
    final_df.to_csv(args.out, index=False)
    print(f"Generated {len(final_df)} records across {args.lots} lots.")
    print(f"Saved to {args.out}")

if __name__ == "__main__":
    main()
