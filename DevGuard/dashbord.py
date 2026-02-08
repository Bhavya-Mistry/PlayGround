import streamlit as st
import pandas as pd
import requests

# 1. Config
st.set_page_config(page_title="DevGuard Monitor", page_icon="🛡️", layout="wide")

st.title("🛡️ DevGuard: Intelligent Code Reviewer")
st.markdown("---")

# 2. The API URL (Make sure this matches your Render URL)
# If you are running locally, use http://localhost:8000
API_URL = "https://devguard-api.onrender.com"

# 3. Sidebar for Controls
st.sidebar.header("Control Panel")
if st.sidebar.button("Refresh Data"):
    st.rerun()

# 4. Fetch Data
try:
    response = requests.get(f"{API_URL}/reviews")

    if response.status_code == 200:
        data = response.json()

        if data:
            # Convert to DataFrame
            df = pd.DataFrame(data)

            # --- TOP METRICS ---
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Reviews", len(df))
            col2.metric("Active Repos", df["repo_name"].nunique())
            # Handle empty data case for Latest PR
            latest_pr = df["pr_number"].iloc[0] if not df.empty else "N/A"
            col3.metric("Latest PR", f"#{latest_pr}")

            # --- RECENT ACTIVITY TABLE ---
            st.subheader("Recent Reviews")
            st.dataframe(
                df[["repo_name", "pr_number", "ai_feedback", "created_at"]],
                use_container_width=True,
                hide_index=True,
            )

            # --- DEEP DIVE (UPDATED) ---
            st.markdown("---")
            st.subheader("🔍 Deep Dive")

            # Create a label for the dropdown that shows PR Number AND Repo Name
            # This is helpful if you have PR #18 in two different repos
            # We create a new column just for the dropdown display
            df["display_label"] = df.apply(
                lambda x: (
                    f"PR #{x['pr_number']} - {x['repo_name']} ({x['created_at']})"
                ),
                axis=1,
            )

            # The user selects from these labels
            selected_label = st.selectbox("Select a PR to Inspect", df["display_label"])

            # We find the row that matches that label
            selected_row = df[df["display_label"] == selected_label].iloc[0]

            # Display the data
            st.info(
                f"Full AI Feedback for PR #{selected_row['pr_number']} in {selected_row['repo_name']}"
            )
            st.markdown("### 🤖 AI Code Review")
            st.code(selected_row["ai_feedback"], language="markdown")

        else:
            st.warning("No reviews found yet. Open a PR to trigger DevGuard!")

    else:
        st.error(f"Failed to fetch data: {response.status_code}")

except Exception as e:
    st.error(f"Error connecting to API: {e}")
