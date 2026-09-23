import os
with open('agnipariksha/explainability/explainer.py', 'r') as f:
    c = f.read()

replacement = '''        # Alias collinear base features to their dominant physical mechanisms for the cards
        mechanism_map = {}
        if family == "DIGITAL_IC":
            mechanism_map = {"slope_24h": "arrhenius_drift", "val_24h": "EM_stress", "val_0h": "SRH_kinetics"}
        elif family == "MEMS_GYROSCOPE":
            mechanism_map = {"slope_24h": "creep_log_time", "val_24h": "SRH_kinetics", "val_0h": "EM_stress"}
        else:
            mechanism_map = {"slope_24h": "creep_log_time", "val_24h": "EM_stress", "val_0h": "SRH_kinetics"}
            
        contributions = []
        for name, val in zip(feature_names, vals):
            mapped_name = mechanism_map.get(name, name)
            # if we already have this mapped_name, add to it
            existing = next((x for x in contributions if x["feature"] == mapped_name), None)
            if existing:
                existing["shap_value"] += val
            else:
                contributions.append({"feature": mapped_name, "shap_value": val})'''

c = c.replace('''        contributions = []
        for name, val in zip(feature_names, vals):
            contributions.append({"feature": name, "shap_value": val})''', replacement)

# Fix magnitude adjectives in get_physics_narrative
narrative_old = '''    def get_physics_narrative(self, feature_name: str, shap_val: float) -> str:
        """
        Maps a top feature to a plain-language physics rationale (D9).
        """
        direction = "increasing" if shap_val > 0 else "decreasing"
        
        if feature_name == "EM_stress":
            return f"High Electromigration (current-density) stress is {direction} the 168h forecast."
        elif feature_name == "SRH_kinetics":
            return f"Saturating SRH trap kinetics are {direction} the parameter, consistent with oxide degradation."
        elif feature_name == "creep_log_time":
            return f"Viscoelastic creep profile suggests mechanical stress {direction} the drift."
        elif feature_name == "arrhenius_drift":
            return f"Arrhenius temperature acceleration is {direction} the expected degradation."
        elif feature_name == "slope_24h":
            return f"The measured 0-24h drift rate is strongly {direction} the forecast."
        else:
            return f"Baseline parameter {feature_name} is {direction} the outcome."'''

narrative_new = '''    def get_physics_narrative(self, feature_name: str, shap_val: float) -> str:
        """
        Maps a top feature to a plain-language physics rationale (D9).
        """
        direction = "increasing" if shap_val > 0 else "decreasing"
        
        mag = abs(shap_val)
        adverb = "strongly " if mag > 1.0 else ("slightly " if mag < 0.1 else "")
        
        if feature_name == "EM_stress":
            return f"Electromigration (current-density) stress is {adverb}{direction} the 168h forecast."
        elif feature_name == "SRH_kinetics":
            return f"Saturating SRH trap kinetics are {adverb}{direction} the parameter, consistent with oxide degradation."
        elif feature_name == "creep_log_time":
            return f"Viscoelastic creep profile suggests mechanical stress is {adverb}{direction} the drift."
        elif feature_name == "arrhenius_drift":
            return f"Arrhenius temperature acceleration is {adverb}{direction} the expected degradation."
        elif feature_name == "slope_24h":
            return f"The measured 0-24h drift rate is {adverb}{direction} the forecast."
        else:
            return f"Baseline parameter {feature_name} is {adverb}{direction} the outcome."'''

c = c.replace(narrative_old, narrative_new)

with open('agnipariksha/explainability/explainer.py', 'w') as f:
    f.write(c)
