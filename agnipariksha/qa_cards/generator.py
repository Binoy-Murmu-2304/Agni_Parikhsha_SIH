"""
QA Justification Card Generator
"""
import os
import pandas as pd
from agnipariksha.config import FAMILY_SPECS
from typing import Dict, Any

class QACardGenerator:
    """
    Generates Markdown disposition cards for QA inspectors (Phase 4.3).
    """
    
    def __init__(self, out_dir: str = "qa_cards_output"):
        self.out_dir = out_dir
        os.makedirs(self.out_dir, exist_ok=True)
        
    def generate_card(self, comp_id: str, family: str, verdict: str, 
                      risk_tier: str, measured_24h: float, pred_168h: float, 
                      margin: float, conformal_90: float, 
                      explanation: Dict[str, Any], explainer,
                      module_a_outlier: bool = False, safety_slope_breach: bool = False,
                      capability_fallback: bool = False) -> str:
        
        conf_str = f"+/- {conformal_90:.2f}" if conformal_90 else "not computed"
        spec = FAMILY_SPECS.get(family, {})
        spec_max = spec.get('spec_max', 0)
        unit = spec.get('unit', '')
        spec_str = ""
        if spec_max:
            if pred_168h > spec_max:
                spec_str = f"{unit} vs Spec Max {spec_max} {unit} ? forecast exceeds limit"
            elif pred_168h > spec_max * 0.9:
                spec_str = f"{unit} vs Spec Max {spec_max} {unit} ? forecast is near limit"
            else:
                spec_str = f"{unit} vs Spec Max {spec_max} {unit}"
                
        md = f"""# AGNI PARIKSHA - QA Disposition Card
**Component ID**: `{comp_id}`
**Family**: `{family}`

## 1. Verdict & Risk Tier
**Verdict**: {verdict}
**Risk Tier**: {risk_tier}

## 2. Quantitative Forecast
- **Measured at 24h**: {measured_24h:.2f}
- **Predicted 168h**: {pred_168h:.2f} {spec_str}
- **Conformal Interval (90%)**: {conf_str}
- **Safety Slope Margin**: {margin:.4f} (allowed - measured max slope)

## 3. Explanability & Physics Trace
"""
        base_val = explanation.get('base_value', 0.0) if explanation else 0.0
        md += f"Base model prediction before features: {base_val:.2f}\n\n**Top Contributing Factors:**\n"
        top_feats = explanation.get('top_features', []) if explanation else []
        if top_feats:
            for feat in top_feats:
                name = feat.get('feature', 'unknown')
                val = feat.get('shap_value', 0.0)
                narrative = explainer.get_physics_narrative(name, val) if explainer else "Feature contribution"
                md += f"- **{name}** (Impact: {val:+.2f}): {narrative}\n"
        else:
            md += "- Explanation physics trace not computed for this record\n"
            

        md += f"\n## Suspected Mechanism (Family Physics Prior)\n"
        if family == "DIGITAL_IC":
            md += "drift pattern consistent with thermally-accelerated leakage growth (Arrhenius-like)\n"
        elif family == "MEMS_GYROSCOPE":
            md += "consistent with mechanical relaxation (viscoelastic creep)\n"
        elif family == "IMAGE_SENSOR":
            md += "consistent with dark-current growth (SRH trap generation)\n"
        elif family == "MIXED_SIGNAL_IC":
            md += "consistent with current-density stress (electromigration-like)\n"
        elif family == "PRECISION_VOLTAGE_REF":
            md += "consistent with thermal stress / hysteresis drift\n"
        md += "\n*Disclaimer: Mechanism hypotheses are family-prior heuristics, not causal identifications.*\n"
        
        if "FULL_BURN_IN" in verdict:
            md += f"\n## Mandatory Routing\n"
            triggers = []
            if module_a_outlier: triggers.append("Module A outlier")
            if safety_slope_breach: triggers.append("Safety slope breach")
            
            if triggers:
                md += f"**Reason**: triggered {', '.join(triggers)}; disposition overridden to FULL_BURN_IN by capability routing policy."
            else:
                md += f"**Reason**: {verdict}. This family/component cannot be certified early. Route to full 168h burn-in."
        else:
            md += f"\n## Recommended Disposition\n"
            if "RED" in verdict:
                md += f"**REJECT**. Drift exceeds safety bounds and conformal coverage cannot guarantee spec compliance."
            elif "MEDIUM" in risk_tier or "FULL_BURN_IN" in verdict:
                md += f"**EXTEND TEST**. Anomalous behavior detected, but not yet failing safety limits. Continue screening."
            else:
                md += f"**PASS (EARLY termination allowed)**. Component is stable and drift trajectory is safely within physical limits."
                
        # Save to file
        file_path = os.path.join(self.out_dir, f"{comp_id}_QA_Card.md")
        with open(file_path, "w") as f:
            f.write(md)
            
        return md
