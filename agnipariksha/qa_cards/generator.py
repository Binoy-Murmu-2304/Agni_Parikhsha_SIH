"""
QA Justification Card Generator
"""
import os
import pandas as pd
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
                      explanation: Dict[str, Any], explainer) -> str:
        
        md = f"""# AGNI PARIKSHA - QA Disposition Card
**Component ID**: `{comp_id}`
**Family**: `{family}`

## 1. Verdict & Risk Tier
**Verdict**: {verdict}
**Risk Tier**: {risk_tier}

## 2. Quantitative Forecast
- **Measured at 24h**: {measured_24h:.2f}
- **Predicted 168h**: {pred_168h:.2f}
- **Conformal Interval (90%)**: +/- {conformal_90:.2f}
- **Safety Slope Margin**: {margin:.4f} (allowed - measured max slope)

## 3. Explanability & Physics Trace
Base model prediction before features: {explanation['base_value']:.2f}

**Top Contributing Factors:**
"""
        for feat in explanation['top_features']:
            name = feat['feature']
            val = feat['shap_value']
            narrative = explainer.get_physics_narrative(name, val)
            md += f"- **{name}** (Impact: {val:+.2f}): {narrative}\n"
            
        if "FULL_BURN_IN" in verdict:
            md += f"\n## Mandatory Routing\n"
            md += f"**Reason**: {verdict}. This family/component cannot be certified early. Route to full 168h burn-in."
        else:
            md += f"\n## Recommended Disposition\n"
            if "RED" in risk_tier:
                md += f"**REJECT**. Drift exceeds safety bounds and conformal coverage cannot guarantee spec compliance."
            elif "YELLOW" in risk_tier:
                md += f"**EXTEND TEST**. Anomalous behavior detected, but not yet failing safety limits. Continue screening."
            else:
                md += f"**PASS (EARLY termination allowed)**. Component is stable and drift trajectory is safely within physical limits."
                
        # Save to file
        file_path = os.path.join(self.out_dir, f"{comp_id}_QA_Card.md")
        with open(file_path, "w") as f:
            f.write(md)
            
        return file_path
