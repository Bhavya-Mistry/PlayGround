import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
# from dataset import load_data


from sklearn.datasets import load_iris
import pandas as pd

def load_data():
    iris = load_iris()
    X = iris.data
    y = iris.target
    feature_names = iris.feature_names
    return X, y, feature_names

def train_and_save_model():
    X, y, _ = load_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy:.2f}")

    # Save model
    joblib.dump(model, "savedmodel/saved_model.pkl")


if __name__ == "__main__":
    train_and_save_model()
