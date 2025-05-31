import streamlit as st
from sklearn.datasets import load_iris
import pandas as pd

st.title("Iris Dataset Viewer")

iris = load_iris()
df = pd.DataFrame(data=iris.data, columns=iris.feature_names)
df['target'] = iris.target

st.write("Here's the Iris dataset:")
st.dataframe(df)

st.write("Basic stats:")
st.write(df.describe())
