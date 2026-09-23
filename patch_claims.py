import pandas as pd

df = pd.read_csv('claims.csv')
df = df[~df['claim_id'].isin(['AGNI.mae_guard', 'AGNI.w_fn_ranking', 'AGNI.min_branch'])]
df.to_csv('claims.csv', index=False)
print("Updated claims.csv")
