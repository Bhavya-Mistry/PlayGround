import streamlit as st
import numpy as np
import pandas as pd
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

st.sidebar.title("Let's Explore the Iris Dataset")
split_bar = st.sidebar.slider("Test Size", 0.1, 0.9, 0.2)


def load_data():
    iris = datasets.load_iris()
    return iris.data, iris.target

def split(split_bar):
    X, y = load_data()
    return train_test_split(X, y, test_size=split_bar, random_state=42)

def train_model(classifier, X_train, y_train):
    if classifier == "KNN":
        from sklearn.neighbors import KNeighborsClassifier
        model = KNeighborsClassifier()
    elif classifier == "SVM":
        from sklearn.svm import SVC
        model = SVC()
    elif classifier == "Random Forest":
        from sklearn.ensemble import RandomForestClassifier
        model = RandomForestClassifier()
    model.fit(X_train, y_train)
    return model

# Sidebar UI
classifier = st.sidebar.selectbox("Select classifier", ["KNN", "SVM", "Random Forest"])
train_button = st.sidebar.button("Let's Start")

# Train + Evaluate
if train_button:
    X_train, X_test, y_train, y_test = split(split_bar)
    model = train_model(classifier, X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    st.success(f"Model trained successfully with {classifier}!")
    st.write(f"Accuracy of the model: **{acc:.2f}**")
