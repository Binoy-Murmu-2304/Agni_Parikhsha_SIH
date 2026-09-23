import os

with open('agnipariksha/qa_cards/generator.py', 'r') as f:
    c = f.read()

old_sig = '''    def generate_card(self, comp_id: str, family: str, verdict: str, 
                      risk_tier: str, measured_24h: float, pred_168h: float, 
                      margin: float, conformal_90: float, 
                      explanation: Dict[str, Any], explainer) -> str:'''

new_sig = '''    def generate_card(self, comp_id: str, family: str, verdict: str, 
                      risk_tier: str, measured_24h: float, pred_168h: float, 
                      margin: float, conformal_90: float, 
                      explanation: Dict[str, Any], explainer,
                      module_a_outlier: bool = False, safety_slope_breach: bool = False,
                      capability_fallback: bool = False) -> str:'''

c = c.replace(old_sig, new_sig)

old_md = '''        if "FULL_BURN_IN" in verdict:
            md += f"\\n## Mandatory Routing\\n"
            md += f"**Reason**: {verdict}. This family/component cannot be certified early. Route to full 168h burn-in."'''

new_md = '''        if "FULL_BURN_IN" in verdict:
            md += f"\\n## Mandatory Routing\\n"
            triggers = []
            if module_a_outlier: triggers.append("Module A outlier")
            if safety_slope_breach: triggers.append("Safety slope breach")
            
            if triggers:
                md += f"**Reason**: triggered {', '.join(triggers)}; disposition overridden to FULL_BURN_IN by capability routing policy."
            else:
                md += f"**Reason**: {verdict}. This family/component cannot be certified early. Route to full 168h burn-in."'''

c = c.replace(old_md, new_md)

# Change return to actually return the md text so the dashboard can use it!
# Wait, it was returning ile_path. If it returns ile_path, how did the dashboard show it?
# In main.py I returned {"markdown": md}, which would be a file path!
c = c.replace('''        return file_path''', '''        return md''')

with open('agnipariksha/qa_cards/generator.py', 'w') as f:
    f.write(c)
