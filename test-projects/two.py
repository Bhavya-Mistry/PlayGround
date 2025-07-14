import pandas as pd

df = pd.read_csv(r"career-navigator\v2\data\dataset.csv")

print(df['Recommended_Career'].unique())