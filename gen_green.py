import pandas as pd
from agnipariksha.module_b.predictor import DriftPredictor
from agnipariksha.explainability.explainer import AgniExplainer
from agnipariksha.qa_cards.generator import QACardGenerator

family = 'DIGITAL_IC'
df_train = pd.DataFrame({'family': [family]*10, 'value_0h': [10.0]*10, 'value_24h': [10.0]*10, 'value_168h': [10.0]*10})
predictor = DriftPredictor()
predictor.fit(df_train, df_train)

df_test = pd.DataFrame({'family': [family], 'value_0h': [10.0], 'value_24h': [10.1]}, index=[0])
df_res = predictor.compute_safety_slope(df_test, current_hour=24)

explainer = AgniExplainer(predictor)
explanation = explainer.explain_instance(df_test, family)

gen = QACardGenerator('test_qa_cards')
gen.generate_card('TEST_COMP_GREEN', family, df_res.loc[0, 'module_b_verdict'], df_res.loc[0, 'module_b_verdict'], 10.1, df_res.loc[0, 'pred_168h'], 0.05, 0.0, explanation, explainer)
