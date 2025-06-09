"""
recommender.py

Module to compute recipe recommendations based on TF-IDF + cosine similarity.
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def get_recommendations(user_ingredients, df, vectorizer, tfidf_matrix, top_n=5):
    """
    Recommend recipes given a list of user ingredients.

    Returns top_n recipes with similarity score and missing ingredients.
    """
    # Prepare user input string
    user_str = ' '.join([ing.strip().lower() for ing in user_ingredients])
    user_vec = vectorizer.transform([user_str])

    # Compute cosine similarity
    sims = cosine_similarity(user_vec, tfidf_matrix).flatten()

    # Get top indices
    idx_sorted = np.argsort(-sims)[:top_n]

    results = []
    for idx in idx_sorted:
        recipe = df.iloc[idx]
        score = sims[idx]
        # Compute missing ingredients
        recipe_ings = set([i.strip() for i in recipe['ingredients'].split(',')])
        missing = list(recipe_ings.difference(set(user_ingredients)))
        results.append({
            'name': recipe['name'],
            'score': round(float(score), 3),
            'missing_ingredients': missing,
            'tags': recipe.get('tags', ''),
            'steps': recipe.get('steps', ''),
            'veg': recipe.get('veg', ''),
            'region': recipe.get('region', ''),
            'time_minutes': recipe.get('time_minutes', '')
        })
    return results