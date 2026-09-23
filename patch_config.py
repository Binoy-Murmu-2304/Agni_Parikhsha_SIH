import os

with open('agnipariksha/config.py', 'r') as f:
    content = f.read()

if "CAPABILITY_ROUTING" not in content:
    content += '''
# Phase 4/5 Capability Audit Routing
# Families where DriftPredictor MAE > 20% of spec_max must never emit GREEN
CAPABILITY_ROUTING = {
    "DIGITAL_IC": "MANDATORY_FULL_BURN_IN",
    "MIXED_SIGNAL_IC": "MANDATORY_FULL_BURN_IN",
    "PRECISION_VOLTAGE_REF": "MANDATORY_FULL_BURN_IN",
    "MEMS_GYROSCOPE": "CAPABLE",
    "IMAGE_SENSOR": "CAPABLE"
}
'''
    with open('agnipariksha/config.py', 'w') as f:
        f.write(content)
