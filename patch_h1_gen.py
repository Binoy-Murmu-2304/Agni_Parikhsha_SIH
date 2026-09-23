import os

with open('agnipariksha/qa_cards/generator.py', 'r') as f:
    c = f.read()

# I need to insert the Suspected Mechanism section before Mandatory Routing / Recommended Disposition.
# The code ends the Top Contributing Factors loop, then does if "FULL_BURN_IN" in verdict:
insert_point = '''        if "FULL_BURN_IN" in verdict:'''

suspected_mechanism_block = '''
        md += f"\\n## Suspected Mechanism (Family Physics Prior)\\n"
        if family == "DIGITAL_IC":
            md += "drift pattern consistent with thermally-accelerated leakage growth (Arrhenius-like)\\n"
        elif family == "MEMS_GYROSCOPE":
            md += "consistent with mechanical relaxation (viscoelastic creep)\\n"
        elif family == "IMAGE_SENSOR":
            md += "consistent with dark-current growth (SRH trap generation)\\n"
        elif family == "MIXED_SIGNAL_IC":
            md += "consistent with current-density stress (electromigration-like)\\n"
        elif family == "PRECISION_VOLTAGE_REF":
            md += "consistent with thermal stress / hysteresis drift\\n"
        md += "\\n*Disclaimer: Mechanism hypotheses are family-prior heuristics, not causal identifications.*\\n"
        
        if "FULL_BURN_IN" in verdict:'''

c = c.replace(insert_point, suspected_mechanism_block)

with open('agnipariksha/qa_cards/generator.py', 'w') as f:
    f.write(c)

