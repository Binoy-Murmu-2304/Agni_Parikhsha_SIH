import shap
import pandas as pd
import numpy as np
from typing import Dict, Any, List

class AgniExplainer:
    """
    Phase 4: Explainability.
    Provides TreeExplainer SHAP values and maps them to physics mechanisms.
    """
    
    def __init__(self, predictor):
        self.predictor = predictor
        self.explainers = {}
        
        # Build explainers for each family model
        for family, model in self.predictor.models.items():
            # HistGradientBoosting isn't perfectly supported by TreeExplainer directly in older shap,
            # but modern shap (or a generic explainer) handles it. We use TreeExplainer if possible,
            # else PermutationExplainer. For robustness we can try TreeExplainer.
            try:
                self.explainers[family] = shap.TreeExplainer(model)
            except Exception:
                # Fallback to a fast generic explainer if TreeExplainer fails on HistGBM
                # We need a background dataset. We will defer initialization to the explain call
                # if we have to use ExactExplainer, or just use the predict function.
                pass

    def explain_instance(self, df_instance: pd.DataFrame, family: str) -> Dict[str, Any]:
        """
        Computes SHAP values for a single component and maps them to physics.
        """
        X = self.predictor.extract_features(df_instance, current_hour=24)
        
        # If no explainer built (fallback needed)
        if family not in self.explainers:
            # We will just use permutation explainer on the fly
            explainer = shap.Explainer(self.predictor.models[family].predict, X)
            shap_values = explainer(X)
            vals = shap_values.values[0]
            base_value = shap_values.base_values[0]
        else:
            explainer = self.explainers[family]
            shap_values = explainer(X)
            # shap_values could be an object or numpy array depending on shap version
            if hasattr(shap_values, 'values'):
                vals = shap_values.values[0]
                base_value = shap_values.base_values[0]
            else:
                vals = shap_values[0]
                base_value = explainer.expected_value
                if isinstance(base_value, (list, np.ndarray)):
                    base_value = base_value[0]
                
        feature_names = list(X.columns)
        
        contributions = []
        for name, val in zip(feature_names, vals):
            contributions.append({"feature": name, "shap_value": val})
            
        # Sort by absolute contribution
        contributions.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
        
        return {
            "base_value": base_value,
            "contributions": contributions,
            "top_features": contributions[:3]
        }
        
    def get_physics_narrative(self, feature_name: str, shap_val: float) -> str:
        """
        Honest feature descriptions with magnitude scaling.
        """
        direction = "increasing" if shap_val > 0 else "decreasing"
        
        mag = abs(shap_val)
        adverb = "strongly " if mag > 1.0 else ("slightly " if mag < 0.1 else "")
        
        if feature_name == "slope_24h":
            return f"The measured 0-24h drift rate is {adverb}{direction} the forecast."
        elif feature_name == "val_24h":
            return f"The parameter level at 24h is {adverb}{direction} the forecast."
        elif feature_name == "val_0h":
            return f"The baseline level at 0h is {adverb}{direction} the forecast."
        else:
            return f"Parameter {feature_name} is {adverb}{direction} the outcome."
