import pandas as pd

df = pd.read_csv('claims.csv')
df = df.iloc[:-3]
df.to_csv('claims.csv', index=False)
