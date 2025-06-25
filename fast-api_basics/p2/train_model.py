import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

df = pd.read_csv("fast-api_basics\p2\Iris.csv")

print(df.head())

print(df.columns)

df.drop('Id', axis=1, inplace=True)

X = df.drop('Species', axis=1)
Y = df['Species']

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=23, test_size=0.2)

model = LogisticRegression()
model.fit(X_train, Y_train)

y_pred_test = model.predict(X_test)
y_pred_train = model.predict(X_train)

print("Test Accuracy Score :", accuracy_score(Y_test, y_pred_test))
print("Train Accuracy Score :", accuracy_score(Y_train, y_pred_train))

joblib.dump(model, "fast-api_basics\p2\iris_logistic_model.pkl")