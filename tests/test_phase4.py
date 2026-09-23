import pytest
import pandas as pd
import numpy as np
import os
from agnipariksha.module_b.predictor import DriftPredictor
from agnipariksha.explainability.explainer import AgniExplainer
from agnipariksha.qa_cards.generator import QACardGenerator

def test_physics_mapping_and_shap():
    """
    Test Phase 4.1, 4.2, 4.3:
    - SHAP runs on a mock component.
    - Physics labels map correctly.
    - QA card is generated.
    """
    # Create mock train data to fit predictor
    family = "IMAGE_SENSOR"
    df_train = pd.DataFrame({
        "family": [family]*100,
        "value_0h": np.random.uniform(5, 10, 100),
        "value_24h": np.random.uniform(6, 11, 100),
        "value_168h": np.random.uniform(7, 15, 100)
    })
    df_cal = df_train.copy()
    
    predictor = DriftPredictor()
    predictor.fit(df_train, df_cal)
    
    explainer = AgniExplainer(predictor)
    
    # Test instance
    df_test = pd.DataFrame({
        "family": [family],
        "value_0h": [8.0],
        "value_24h": [9.0]
    }, index=[0])
    
    # Compute safety slope to get margins
    df_res = predictor.compute_safety_slope(df_test, current_hour=24)
    pred_168h = df_res.loc[0, "pred_168h"]
    margin = df_res.loc[0, "allowed_slope"] - max(df_res.loc[0, "measured_slope"], df_res.loc[0, "pred_slope"])
    verdict = df_res.loc[0, "module_b_verdict"]
    
    # Run explainability
    explanation = explainer.explain_instance(df_test, family)
    
    assert "base_value" in explanation
    assert "top_features" in explanation
    assert len(explanation["top_features"]) <= 3
    
    # Verify physics narrative works for one of the extracted features
    feat_name = explanation["top_features"][0]["feature"]
    narrative = explainer.get_physics_narrative(feat_name, 0.5)
    assert narrative != ""
    assert "increasing" in narrative or "decreasing" in narrative
    
    # Generate QA Card
    card_gen = QACardGenerator(out_dir="test_qa_cards")
    comp_id = "TEST_COMP_001"
    filepath = card_gen.generate_card(
        comp_id=comp_id,
        family=family,
        verdict=verdict,
        risk_tier=verdict,
        measured_24h=9.0,
        pred_168h=pred_168h,
        margin=margin,
        conformal_90=predictor.q_alphas_90.get(family, 0),
        explanation=explanation,
        explainer=explainer
    )
    
    content = filepath
    assert "AGNI PARIKSHA - QA Disposition Card" in content
    assert comp_id in content
