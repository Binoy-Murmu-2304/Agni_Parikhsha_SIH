"""
Stress Tester (Phase 5.4)
"""
import pandas as pd
from typing import Dict, Any

class StressTester:
    def __init__(self, evaluator, module_a, module_b):
        self.evaluator = evaluator
        self.module_a = module_a
        self.module_b = module_b
        
    def evaluate_stress_set(self, df_stress: pd.DataFrame, k_noise: float = 3.5) -> Dict[str, Any]:
        """
        Runs the frozen model on the generator-independent stress set.
        """
        mechanisms = df_stress['mechanism'].unique()
        
        # We need to reconstruct effect sizes. The generator creates lot_id like STRESS_mech_size_family
        results = {}
        failure_envelopes = []
        
        for mech in mechanisms:
            df_mech = df_stress[df_stress['mechanism'] == mech].copy()
            
            # Extract effect size. lot_id is formatted as STRESS_{mech}_{size}_{family}
            # Since mech can have underscores, we remove "STRESS_{mech}_" from the start.
            def extract_size(lot_id):
                remainder = lot_id.replace(f"STRESS_{mech}_", "")
                return float(remainder.split("_")[0])
            df_mech['effect_size'] = df_mech['lot_id'].apply(extract_size)
            
            sizes = sorted(df_mech['effect_size'].unique())
            
            detection_rates = {}
            mde_50, mde_90, mde_100 = None, None, None
            
            for size in sizes:
                df_size = df_mech[df_mech['effect_size'] == size]
                
                # Run through pipeline
                dfs_res = []
                # Group by lot (each family has 100 parts per size)
                for lot_id, lot_data in df_size.groupby("lot_id"):
                    dfs_res.append(self.evaluator.end_to_end_disposition(lot_data, self.module_a, self.module_b, k_noise=k_noise))
                    
                df_res = pd.concat(dfs_res)
                
                n_total = len(df_res)
                n_detected = df_res['final_flag'].sum()
                rate = n_detected / n_total if n_total > 0 else 0
                
                detection_rates[size] = rate
                
                if rate >= 0.5 and mde_50 is None: mde_50 = size
                if rate >= 0.9 and mde_90 is None: mde_90 = size
                if rate == 1.0 and mde_100 is None: mde_100 = size
                
            results[mech] = {
                "detection_rates": detection_rates,
                "mde_50": mde_50,
                "mde_90": mde_90,
                "mde_100": mde_100
            }
            
            # Construct failure envelope sentence
            if mde_100 is None:
                fail_size = sizes[-1]
                env = f"Misses {mech} defects entirely at effect sizes up to {fail_size}x injected after baseline."
            else:
                fail_size = sizes[sizes.index(mde_100) - 1] if sizes.index(mde_100) > 0 else "< minimum tested"
                env = f"Misses {mech} defects at effect sizes < {fail_size}x injected after baseline."
            failure_envelopes.append(env)
            
        return {
            "tables": results,
            "failure_envelopes": failure_envelopes
        }
