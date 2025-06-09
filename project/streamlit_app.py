"""
streamlit_app.py

Streamlit UI for the Smart Indian Recipe Recommender.
Adapted for Indian Food 101 dataset columns.
"""
import streamlit as st
import pandas as pd
from preprocess import load_data, build_tfidf_matrix
from recommender import get_recommendations

# --- Load and prepare data ---
@st.cache_data
def load_resources():
    df = load_data()
    # Calculate total_time as sum of prep_time + cook_time
    df['prep_time'] = pd.to_numeric(df['prep_time'], errors='coerce').fillna(0)
    df['cook_time'] = pd.to_numeric(df['cook_time'], errors='coerce').fillna(0)
    df['total_time'] = df['prep_time'] + df['cook_time']

    vectorizer, tfidf_matrix = build_tfidf_matrix(df)
    # Extract unique ingredients for selection
    all_ings = sorted({ing.strip() for sub in df['ingredients'] for ing in sub.split(',')})
    return df, vectorizer, tfidf_matrix, all_ings

# Load resources once
df, vectorizer, tfidf_matrix, all_ings = load_resources()

# --- Sidebar ---
st.sidebar.title("🔍 Find Your Recipe")

selected_ings = st.sidebar.multiselect(
    "Select ingredients you have:", all_ings
)

num_rec = st.sidebar.slider("Number of recipes:", 1, 10, 5)
veg_filter = st.sidebar.checkbox("Vegetarian only")
time_limit = st.sidebar.number_input(
    "Max cooking time (minutes):", min_value=10, max_value=240, value=60
)

# --- Filter DataFrame ---
filtered_df = df.copy()

if veg_filter:
    filtered_df = filtered_df[filtered_df['diet'].str.lower() == 'vegetarian']

filtered_df = filtered_df[filtered_df['total_time'] <= time_limit]

filtered_vec_df = filtered_df.reset_index(drop=True)

# Rebuild TF-IDF for filtered data
vectorizer_filt, tfidf_filt = build_tfidf_matrix(filtered_vec_df)

# --- Recommendation ---
if st.sidebar.button("Recommend Recipes"):
    if not selected_ings:
        st.warning("Please select at least one ingredient.")
    else:
        recs = get_recommendations(selected_ings, filtered_vec_df, vectorizer_filt, tfidf_filt, top_n=num_rec)
        st.header("Top Recipe Matches")
        for r in recs:
            st.subheader(f"{r['name']} ({r['score']*100:.1f}% match)")
            st.write(f"**Missing Ingredients:** {', '.join(r['missing_ingredients']) or 'None'}")
            st.write(
                f"**Diet:** {r['veg'] or r.get('diet', 'N/A')} | "
                f"**Total Time:** {r['time_minutes'] or r.get('total_time', 'N/A')} min"
            )
            with st.expander("View Steps & Tags"):
                st.write(r['steps'])
                st.write(f"**Tags:** {r['tags']}")

# --- Footer ---
st.markdown("---")

