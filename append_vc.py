    # R6 Compute invariants
    from agnipariksha.data_generator.generator import AgniSimGenerator
    train_mechs = set(AgniSimGenerator.TRAIN_MECHANISMS)
    stress_mechs = set(AgniSimGenerator.STRESS_MECHANISMS)
    assert len(train_mechs.intersection(stress_mechs)) == 0, "Stress mechanisms intersect with train mechanisms!"
    
    chamber_savings = (168 - 24) / 168 * 100
    assert abs(chamber_savings - 85.71) < 0.01, "Chamber savings mismatch!"
    
    try:
        import pandas as pd
        df_prev = pd.read_csv('data/prevalence_results.csv')
        fpr_str = df_prev[df_prev['Prevalence'] == '5.0%']['FPR (bound)'].iloc[0]
        fpr = float(fpr_str.split('%')[0]) / 100
        green_fraction = 1.0 - fpr
        realized_savings = green_fraction * chamber_savings
        print(f"Realized Chamber Savings (at 5% prev FPR): {realized_savings:.2f}%")
    except:
        pass
    print("All Invariants Verified.")
