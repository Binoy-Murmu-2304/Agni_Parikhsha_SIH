# AGNI-SIM Data Card

**Dataset Name**: AGNI-SIM Synthetic Component Degradation Dataset

## 1. Description and Intent
AGNI-SIM is a synthetic dataset generator created for the AGNI PARIKSHA system. It produces time-series parametric data for 5 component families across 4 checkpoints (0h, 24h, 96h, 168h).

> **IMPORTANT**: AGNI-SIM is synthetic. It proves pipeline correctness and relative method behavior. It does NOT prove field performance on real silicon.

## 2. Distributions & Families
The generator simulates physics-informed baseline drift and realistic unit variances:
- **DIGITAL_IC**: Iddq standby leakage (µA). Drift modeled linearly.
- **MIXED_SIGNAL_IC**: Leakage current (µA). Drift modeled linearly.
- **MEMS_GYROSCOPE**: Bias drift rate (dps). Viscoelastic creep modeled logarithmically.
- **PRECISION_VOLTAGE_REF**: Drift (µV). Modeled linearly.
- **IMAGE_SENSOR**: Dark current (nA/cm²). Saturating SRH kinetics modeled as $f(t) = A(1 - e^{-t/\tau})$.

Noise is additive Gaussian with $\sigma = \text{spec\_max} \times 0.01$.

## 3. Defect Mechanisms
The data includes exactly 3 defect mechanisms in the visible dataset (Train/Calibration/Blind) and 6 reserved mechanisms strictly for the stress set.

### Train/Visible Mechanisms (15% prevalence)
1. **EXCESSIVE_DRIFT**: Accelerated physics drift rate.
2. **OFFSET_SHIFT**: Higher baseline starting value.
3. **INTERMITTENT_JUMP**: Random jump at a single checkpoint >0h.

### Reserved Stress Mechanisms (Evaluated only in Phase 5)
1. **DELAYED_STEP**: Step change after 24h.
2. **NON_MONOTONIC**: Value goes up at 96h, then down at 168h.
3. **SLOW_CREEP**: Subtle steady rise.
4. **LATE_AVALANCHE**: Sudden massive spike at 168h.
5. **EARLY_SATURATION**: Peaks early but at a high failure level.
6. **NOISY_SIGNAL**: Extreme measurement variance but normal mean.

## 4. Dataset Layout
- **Lot Structure**: 2,000 components per lot.
- **Splits**: Train (60%), Calibration (20%), Blind_Test (20%).
- **Disjointness**: Splits are completely disjoint at the LOT level (a lot in Train will never appear in Calibration).
