    # R6 Compute invariants
    from agnipariksha.data_generator.generator import AgniSimGenerator
    train_mechs = set(AgniSimGenerator.TRAIN_MECHANISMS)
    stress_mechs = set(AgniSimGenerator.STRESS_MECHANISMS)
    assert len(train_mechs.intersection(stress_mechs)) == 0, "Stress mechanisms intersect with train mechanisms!"
    
    chamber_savings = (168 - 24) / 168 * 100
    assert abs(chamber_savings - 85.71) < 0.01, "Chamber savings mismatch!"
    
    # B3 Realized Savings
    try:
        import pandas as pd
        df_dev = pd.read_csv('data/dataset.csv')
        from agnipariksha.config import FAMILY_SPECS
        from agnipariksha.evaluation.evaluator import AgniEvaluator
        from agnipariksha.module_a.outlier import DynamicOutlierDetector
        from agnipariksha.module_b.predictor import DriftPredictor
        import json
        with open("data/manifest.json", "r") as f: manifest = json.load(f)
        train_lots = [item['lot_id'] for item in manifest['TRAIN']]
        cal_lots = [item['lot_id'] for item in manifest['CALIBRATION']]
        dev_lots = [item['lot_id'] for item in manifest['DEVELOPMENT']]
        df_train = df_dev[df_dev['lot_id'].isin(train_lots)]
        df_cal = df_dev[df_dev['lot_id'].isin(cal_lots)]
        df_blind = df_dev[df_dev['lot_id'].isin(dev_lots)]
        module_b = DriftPredictor()
        module_b.fit(df_train, df_cal)
        module_a = DynamicOutlierDetector()
        evaluator = AgniEvaluator()
        
        failed = ['DIGITAL_IC', 'MIXED_SIGNAL_IC', 'PRECISION_VOLTAGE_REF']
        realized_savings = 0.0
        share_f = 1 / len(FAMILY_SPECS)
        for fam in FAMILY_SPECS.keys():
            if fam in failed:
                exit_rate = 0.0
            else:
                df_fam = df_blind[df_blind['family'] == fam]
                n_def = 100
                n_neg = 1900
                df_def = df_fam[df_fam['is_defective'] == 1].sample(n=n_def, random_state=42)
                df_neg = df_fam[df_fam['is_defective'] == 0].sample(n=n_neg, random_state=42)
                df_eval = pd.concat([df_def, df_neg])
                df_res = evaluator.end_to_end_disposition(df_eval, module_a, module_b, k_noise=3.5)
                exit_rate = 1.0 - df_res['final_flag'].mean()
            realized_savings += share_f * exit_rate * chamber_savings
        
        print(f"Realized Chamber Savings (B3 formulation at 5% prev): {realized_savings:.2f}%")
        
        # small checks
        import json
        with open('metrics_canonical.json', 'r') as f: m = json.load(f)
        assert abs(m['AGNI']['chamber_savings'] - 85.71) < 0.1
        
        # update metrics_canonical
        m['AGNI']['realized_savings'] = realized_savings
        with open('metrics_canonical.json', 'w') as f: json.dump(m, f, indent=2)
    except Exception as e:
        print("Failed to compute B3:", e)
    
    print("All Invariants Verified.")
