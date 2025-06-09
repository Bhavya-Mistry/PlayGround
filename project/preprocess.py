"""
preprocess.py

Loads and cleans the recipe dataset. Extracts ingredients and prepares TF-IDF matrix.
"""
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


def load_data(path="data/recipes.csv"):
    """Load recipes CSV into DataFrame."""
    df = pd.read_csv(path)
    # Ensure consistent lowercasing
    df['ingredients'] = df['ingredients'].str.lower()
    # Split comma-separated into space-separated for TF-IDF
    df['ingredient_str'] = df['ingredients'].str.replace(',', ' ')
    return df


def build_tfidf_matrix(df, max_features=5000):
    """Fit TF-IDF on ingredient strings and return vectorizer + matrix."""
    vectorizer = TfidfVectorizer(max_features=max_features, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(df['ingredient_str'])
    return vectorizer, tfidf_matrix