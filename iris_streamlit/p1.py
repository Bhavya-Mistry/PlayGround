import streamlit as st
import numpy as np
import pandas as pd
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import seaborn as sns

st.title("🌸 Iris Classifier Explorer")

preview = st.checkbox("Show Data Preview")


dataset = datasets.load_iris()
X = dataset.data
y = dataset.target

df = pd.DataFrame(X, columns=dataset.feature_names)

features = dataset.feature_names
class_names = dataset.target_names

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=42)

if preview:
    st.dataframe(df)

classifier = st.selectbox("Select Classifier", ["KNN", "SVM", "Random Forest"])

if classifier == "KNN":
    model = KNeighborsClassifier()
elif classifier == "SVM":
    model = SVC()  
elif classifier == "Random Forest":
    model = RandomForestClassifier()

train = st.button("Train Model")
if train:
    model.fit(X_train, y_train)    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    st.write(f"Accuracy: {accuracy:.2f}")
    # Display confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(10, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', xticklabels=class_names, yticklabels=class_names)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    st.pyplot(plt.gcf())
    
    from sklearn.metrics import classification_report

    report = classification_report(y_test, y_pred, target_names=class_names, output_dict=True)
    report_df = pd.DataFrame(report).transpose()
    st.subheader("Classification Report")
    st.dataframe(report_df)
