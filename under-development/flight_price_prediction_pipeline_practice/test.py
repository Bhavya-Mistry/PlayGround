import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeRegressor


df = pd.read_excel(r"flight_price_prediction\Dataset\Flight-price-predication.xlsx")

df.head()


df['Date_of_Journey'] = pd.to_datetime(df['Date_of_Journey'], format='%d/%m/%Y')
df['Day'] = df['Date_of_Journey'].dt.day_name()

def weekdayornot(x):
    return "Weekend" if x in ["Sunday", "Saturday"] else "Weekday"
df['weekdayornot'] = df['Day'].apply(weekdayornot)

df.drop(['Date_of_Journey', 'Day', 'Dep_Time', 'Arrival_Time', 'Route'], axis=1, inplace=True)

df.dropna(inplace=True)

def con_to_mins(z):
    hrs = 0
    mins = 0
    if 'h' in z:
        hrs = int(z.split('h')[0])
    if 'm' in z:
        mins = int(z.split('m')[0].split()[-1])
    return hrs * 60 + mins

df['Duration'] = df['Duration'].apply(con_to_mins)

df_encoded = pd.get_dummies(df, columns=['Airline', 'Source', 'Destination', 'Total_Stops', 'Additional_Info', 'weekdayornot'], drop_first=True)

df_encoded.head()


X = df_encoded.drop("Price", axis=1)
y = df_encoded["Price"]

x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=23062005)


scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(x_train)
X_test_scaled = scaler.transform(x_test)


lr = LinearRegression()
lr.fit(x_train, y_train)

y_pred = lr.predict(x_test)


r2_lr = r2_score(y_test, y_pred)
mae_lr = mean_absolute_error(y_test, y_pred)
mse_lr = mean_squared_error(y_test, y_pred)
rmse_lr = np.sqrt(mse_lr)
mape_lr = np.mean(np.abs((y_test - y_pred) / y_test)) * 100

print("R² Score:", r2_lr*100)
print("MAE:", mae_lr)
print("MSE:", mse_lr)
print("RMSE:", rmse_lr)
print("MAPE:", mape_lr, "%")


dt = DecisionTreeRegressor(random_state=23062005)

param_grid = {
    'max_depth': [5, 10, 15, 20, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'max_features': ['sqrt', 'log2', None]
}

grid_search = GridSearchCV(estimator=dt, param_grid=param_grid, cv=5, n_jobs=-1, verbose=2)
grid_search.fit(X_train_scaled, y_train)

print(f"Best Parameters: {grid_search.best_params_}")

best_model = grid_search.best_estimator_

y_pred = best_model.predict(X_test_scaled)



r2_dt = r2_score(y_test, y_pred)
mae_dt = mean_absolute_error(y_test, y_pred)
mse_dt = mean_squared_error(y_test, y_pred)
rmse_dt = np.sqrt(mse_dt)
mape_dt = np.mean(np.abs((y_test - y_pred) / y_test)) * 100

print(f"R² Score: {r2_dt * 100:.2f}")
print(f"MAE: {mae_dt:.2f}")
print(f"MSE: {mse_dt:.2f}")
print(f"RMSE: {rmse_dt:.2f}")
print(f"MAPE: {mape_dt:.2f} %")



print("-"*1000)
print(x_train.columns)
print("-"*1000)
print(df_encoded.head())