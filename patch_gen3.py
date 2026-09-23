import os

with open('agnipariksha/qa_cards/generator.py', 'r') as f:
    c = f.read()

c = c.replace('import pandas as pd', 'import pandas as pd\nfrom agnipariksha.config import FAMILY_SPECS')

old_md_start = '''- **Predicted 168h**: {pred_168h:.2f}
- **Conformal Interval (90%)**: +/- {conformal_90:.2f}
- **Safety Slope Margin**: {margin:.4f} (allowed - measured max slope)'''

new_md_start = '''- **Predicted 168h**: {pred_168h:.2f} {spec_str}
- **Conformal Interval (90%)**: {conf_str}
- **Safety Slope Margin**: {margin:.4f} (allowed - measured max slope)'''

c = c.replace(old_md_start, new_md_start)

old_sig = '''                      margin: float, conformal_90: float, 
                      explanation: Dict[str, Any], explainer,'''

new_sig = '''                      margin: float, conformal_90: float, 
                      explanation: Dict[str, Any], explainer,'''

# We need to construct spec_str and conf_str in generate_card
old_func_start = '''        md = f"""# AGNI PARIKSHA - QA Disposition Card'''

new_func_start = '''        conf_str = f"+/- {conformal_90:.2f}" if conformal_90 else "not computed"
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
                
        md = f"""# AGNI PARIKSHA - QA Disposition Card'''

c = c.replace(old_func_start, new_func_start)

with open('agnipariksha/qa_cards/generator.py', 'w') as f:
    f.write(c)
