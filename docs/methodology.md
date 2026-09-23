# Methodology & Derivations

This document traces the mathematical derivations for AGNI PARIKSHA's core algorithms, adhering to Design Principle D4 (No Hardcoded Magic Thresholds) and D9 (Mechanistic Explainability).

## 1. Dynamic Outlier Detection (Module A)

### Robust Statistics
Traditional mean and standard deviation are highly susceptible to outliers. We use the median and Median Absolute Deviation (MAD).
$$ \text{MAD} = \text{median}(|X_i - \text{median}(X)|) $$

### Robust Z-Score
To scale MAD to be consistent with standard deviation (assuming a normal distribution), we multiply by the scaling factor $1.4826$.
$$ Z_{robust} = \frac{|x_i - \text{median}(X)|}{1.4826 \times \text{MAD}} $$
- **Thresholds**: We use $Z_{yellow} = 3.5$ and $Z_{red} = 5.0$.

## 2. Safety Slope (Module B)

The safety slope is the maximum allowed drift rate. It is computed dynamically per component based on the BINDING (minimum) of two physical constraints, plus a lot-statistical bound.

$$ \text{headroom\_bound} = \frac{\text{SpecMax} - Y_{24}}{\text{remaining\_hours}} $$
$$ \text{relative\_bound} = \frac{k_{rel} \times \text{SpecMax}}{168} $$
$$ \text{ALLOWED\_SLOPE} = \min(\text{headroom\_bound}, \text{relative\_bound}) $$

Where $k_{rel} = 0.10$ (allowing a maximum drift of 10% of the entire spec range over a full 168h lifecycle).

### Worked Example 1: DIGITAL_IC (Near-Limit Case)
- **SpecMax**: 50.0 µA
- **Component Readings**: $Y_0 = 47.0$ µA, $Y_{24} = 47.5$ µA
- **Measured Slope**: $(47.5 - 47.0) / 24 = 0.0208$ µA/h
- **Remaining Hours**: $168 - 24 = 144$
- **Headroom Bound**: $(50.0 - 47.5) / 144 = 0.0173$ µA/h
- **Relative Bound**: $(0.10 \times 50.0) / 168 = 0.0297$ µA/h
- **ALLOWED_SLOPE** = $\min(0.0173, 0.0297) = 0.0173$ µA/h

**Verdict**: The measured slope (0.0208) EXCEEDS the allowed slope (0.0173). The component is flagged **RED** (Escalate) before reaching 168h, preventing a field failure.

### Worked Example 2: MEMS_GYROSCOPE (Sub-Limit Abnormal Drift)
- **SpecMax**: 0.5 dps
- **Component Readings**: $Y_0 = 0.1$ dps, $Y_{24} = 0.2$ dps
- **Measured Slope**: $(0.2 - 0.1) / 24 = 0.0041$ dps/h
- **Remaining Hours**: 144
- **Headroom Bound**: $(0.5 - 0.2) / 144 = 0.00208$ dps/h
- **Relative Bound**: $(0.10 \times 0.5) / 168 = 0.000297$ dps/h
- **ALLOWED_SLOPE** = $\min(0.00208, 0.000297) = 0.000297$ dps/h

**Verdict**: The measured slope (0.0041) massively EXCEEDS the allowed relative bound (0.000297). Despite $Y_{24}$ being well below the absolute limit of 0.5, the component is flagged **RED**.

## 3. Conformal Prediction
We compute the empirical residual quantiles $q_{\alpha}$ on the CALIBRATION set to construct conformal prediction intervals.
$$ C(X_{test}) = [\hat{f}(X_{test}) - q_{\alpha}, \hat{f}(X_{test}) + q_{\alpha}] $$
We report coverage at $\alpha = 0.10$ (90%) and $\alpha = 0.05$ (95%).

## 4. Degraded Mode Matrix
| Available Checkpoints | Output | Confidence |
|---|---|---|
| {0h, 24h} | 168h Prediction + Conformal | High |
| {0h, 24h, 96h} | 168h Prediction + Conformal | Very High |
| {0h} (Missing 24h) | Route to FULL_BURN_IN | None |

