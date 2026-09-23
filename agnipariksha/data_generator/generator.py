import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
from ..config import SEED, FAMILY_SPECS

class AgniSimGenerator:
    """
    AGNI-SIM: Synthetic Data Generator for AGNI PARIKSHA.
    """
    CHECKPOINTS = [0, 24, 96, 168]
    
    TRAIN_MECHANISMS = ["EXCESSIVE_DRIFT", "OFFSET_SHIFT", "INTERMITTENT_JUMP"]
    STRESS_MECHANISMS = [
        "DELAYED_STEP", "NON_MONOTONIC", "SLOW_CREEP", 
        "LATE_AVALANCHE", "EARLY_SATURATION", "NOISY_SIGNAL"
    ]

    def __init__(self, seed: int = SEED):
        self.seed = seed
        self.rng = np.random.default_rng(self.seed)

    def _physics_drift(self, family: str, t: float, healthy: bool, mech: str = "NONE", effect_size: float = 1.0) -> float:
        """
        Physics-informed healthy drift formulas per family.
        """
        spec = FAMILY_SPECS[family]["spec_max"]
        
        # Base healthy params
        base_val = spec * self.rng.uniform(0.1, 0.3)
        drift_rate = spec * self.rng.uniform(0.001, 0.005) # normal drift
        
        # Apply defect modifiers
        if not healthy:
            if mech == "OFFSET_SHIFT":
                base_val = spec * self.rng.uniform(0.7, 0.9) * effect_size
            elif mech == "EXCESSIVE_DRIFT":
                drift_rate = spec * self.rng.uniform(0.015, 0.03) * effect_size
        
        val = base_val
        
        if family in ["DIGITAL_IC", "MIXED_SIGNAL_IC"]:
            # Arrhenius-like pseudo exponential or linear drift
            val += drift_rate * t
        elif family == "MEMS_GYROSCOPE":
            # Viscoelastic creep: log-time feature
            val += drift_rate * np.log1p(t) * 10
        elif family == "IMAGE_SENSOR":
            # Saturating SRH kinetics: f(t) = A(1 - exp(-t/tau))
            A = drift_rate * 100
            tau = 50.0
            val += A * (1 - np.exp(-t / tau))
        elif family == "PRECISION_VOLTAGE_REF":
            # Linear drift
            val += drift_rate * t
        else:
            val += drift_rate * t

        # Special time-dependent mechanisms
        if not healthy:
            if mech == "INTERMITTENT_JUMP" and t > 0:
                # 30% chance to jump at any given >0 checkpoint
                if self.rng.random() < 0.3:
                    val += spec * self.rng.uniform(0.4, 0.8) * effect_size
            elif mech == "DELAYED_STEP":
                if t > 24:
                    val += spec * self.rng.uniform(0.5, 0.8) * effect_size
            elif mech == "NON_MONOTONIC":
                if t == 96:
                    val += spec * 0.6 * effect_size
                elif t == 168:
                    val -= spec * 0.4 * effect_size
            elif mech == "SLOW_CREEP":
                val += drift_rate * t * 1.5 * effect_size
            elif mech == "LATE_AVALANCHE":
                if t == 168:
                    val += spec * 2.0 * effect_size
            elif mech == "EARLY_SATURATION":
                val = base_val + (spec * 0.9 * effect_size) * (1 - np.exp(-t / 10.0))
            elif mech == "NOISY_SIGNAL":
                val += self.rng.normal(0, spec * 0.3 * effect_size)

        # Add generic measurement noise
        noise = self.rng.normal(0, spec * 0.01)
        return max(0.0, val + noise)  # usually positive values

    def generate_lot(self, lot_id: str, family: str, n_components: int = 2000, 
                     defect_rate: float = 0.15, is_stress: bool = False, 
                     stress_mech: Optional[str] = None, effect_size: float = 1.0) -> pd.DataFrame:
        """
        Generates a lot of components.
        If is_stress=True, overrides normal defect generation and forces specific stress_mech.
        """
        n_defects = int(n_components * defect_rate)
        n_healthy = n_components - n_defects
        
        labels = [0] * n_healthy + [1] * n_defects
        self.rng.shuffle(labels)
        
        data = []
        for i, is_defective in enumerate(labels):
            comp_id = f"{lot_id}_{i:04d}"
            
            mech = "NONE"
            if is_defective:
                if is_stress:
                    mech = stress_mech
                else:
                    mech = self.rng.choice(self.TRAIN_MECHANISMS)
                    
            row = {
                "component_id": comp_id,
                "lot_id": lot_id,
                "family": family,
                "is_defective": is_defective,
                "mechanism": mech
            }
            
            for t in self.CHECKPOINTS:
                row[f"value_{t}h"] = self._physics_drift(family, t, not is_defective, mech, effect_size)
                
            data.append(row)
            
        return pd.DataFrame(data)

    def generate_dataset(self, num_lots: int = 50, components_per_lot: int = 2000) -> Tuple[pd.DataFrame, Dict]:
        """
        Generates Train/Cal/Blind splits.
        """
        lots = []
        manifest = {
            "TRAIN": [],
            "CALIBRATION": [],
            "BLIND_TEST": []
        }
        
        families = list(FAMILY_SPECS.keys())
        
        lot_idx = 0
        for split, ratio in [("TRAIN", 0.6), ("CALIBRATION", 0.2), ("BLIND_TEST", 0.2)]:
            n_split_lots = int(num_lots * ratio)
            for _ in range(n_split_lots):
                lot_id = f"LOT_{lot_idx:04d}"
                family = families[lot_idx % len(families)]
                
                # Introduce slight lot-to-lot variance in base parameters by re-seeding slightly?
                # The prompt mentions lot-to-lot shift. We achieve this implicitly if the rng state 
                # produces correlated base values, or we can add a lot-level offset.
                lot_offset = self.rng.normal(0, FAMILY_SPECS[family]["spec_max"] * 0.05)
                
                df_lot = self.generate_lot(lot_id, family, n_components=components_per_lot)
                
                # Apply lot offset to all values
                for t in self.CHECKPOINTS:
                    df_lot[f"value_{t}h"] += lot_offset
                    df_lot[f"value_{t}h"] = df_lot[f"value_{t}h"].clip(lower=0)
                
                lots.append(df_lot)
                manifest[split].append({"lot_id": lot_id, "family": family})
                lot_idx += 1
                
        df_all = pd.concat(lots, ignore_index=True)
        return df_all, manifest

    def generate_stress_set(self, components_per_mech: int = 100) -> pd.DataFrame:
        """
        Generates the independent stress set with 6 reserved mechanisms × 6 effect sizes.
        """
        effect_sizes = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        stress_data = []
        
        families = list(FAMILY_SPECS.keys())
        
        idx = 0
        for mech in self.STRESS_MECHANISMS:
            for size in effect_sizes:
                for family in families:
                    # Treat each combination as a mini-lot for tracing
                    lot_id = f"STRESS_{mech}_{size}_{family}"
                    # 100% defective in stress set to test detection vs magnitude
                    df_lot = self.generate_lot(
                        lot_id, family, 
                        n_components=components_per_mech, 
                        defect_rate=1.0, 
                        is_stress=True, 
                        stress_mech=mech, 
                        effect_size=size
                    )
                    stress_data.append(df_lot)
                    idx += 1
                    
        return pd.concat(stress_data, ignore_index=True)
