import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeRegressor


df = pd.read_excel(r"flight_price_prediction\Dataset\Flight-price-predication.xlsx")

print(df.head())
print(df.dtypes)


def con_to_mins(z):
    hrs = 0
    mins = 0
    if 'h' in z:
        hrs = int(z.split('h')[0])
    if 'm' in z:
        mins = int(z.split('m')[0].split()[-1])
    return hrs * 60 + mins



def preprocess_data(df):
    df['Date_of_Journey'] = pd.to_datetime(df['Date_of_Journey'], format='%d/%m/%Y')
    df['Day'] = df['Date_of_Journey'].dt.day_name()
    df['weekdayornot'] = df['Day'].apply(lambda x: "Weekend" if x in ["Sunday","Saturday"] else "Weekday")
    df.drop(['Date_of_Journey', 'Day', 'Dep_Time', 'Arrival_Time', 'Route'], axis=1, inplace=True)
    df.dropna(inplace=True)
    df['Duration'] = df['Duration'].apply(con_to_mins)
    df_encoded = pd.get_dummies(df, columns=['Airline', 'Source', 'Destination', 'Total_Stops', 'Additional_Info', 'weekdayornot'], drop_first=True)
    return df

preprocess_data(df)
print(df.head())


X = df.drop('Price', axis=1)
y = df['Price']


categorical = ['Airline', 'Source', 'Destination', 'Total_Stops', 'Additional_Info', 'weekdayornot']
numerical = ['Duration']


print(df.dtypes)


print("PipeLine Started....")
preprocessor = ColumnTransformer([
    ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), categorical)
])