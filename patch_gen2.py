import os
with open('agnipariksha/qa_cards/generator.py', 'r') as f:
    c = f.read()
c = c.replace('if "RED" in risk_tier:', 'if "RED" in verdict:')
c = c.replace('elif "YELLOW" in risk_tier:', 'elif "MEDIUM" in risk_tier or "FULL_BURN_IN" in verdict:')
with open('agnipariksha/qa_cards/generator.py', 'w') as f:
    f.write(c)
