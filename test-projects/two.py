import pandas as pd

df = pd.read_csv(r"career-navigator\v2\data\generated_career_data.csv")

print(df['Recommended_Career'].unique())