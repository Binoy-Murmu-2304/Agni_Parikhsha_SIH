import pandas as pd
df = pd.read_csv('data/dataset.csv')
for lot in df['lot_id'].unique():
    l = df[df['lot_id'] == lot]
    def_count = l['is_defective'].sum()
    if def_count > 0:
        print(lot, len(l), def_count)
