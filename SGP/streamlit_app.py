import streamlit as st
import requests
import json
import time

# --- Configuration ---
FASTAPI_BASE_URL = "http://localhost:8000/api/v1" # Replace with your deployed backend URL

# --- Streamlit Session State Management ---
if 'question' not in st.session_state:
    st.session_state.question = None
if 'user_answer' not in st.session_state:
    st.session_state.user_answer = ""
if 'feedback' not in st.session_state:
    st.session_state.feedback = None
if 'interview_category' not in st.session_state:
    st.session_state.interview_category = "HR" # Default category
if 'show_ideal_answer' not in st.session_state:
    st.session_state.show_ideal_answer = False
if 'interview_history' not in st.session_state:
    st.session_state.interview_history = [] # To store questions and feedback

# --- FastAPI Interaction Functions ---
def get_random_question(category: str):
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/questions/random/{category}")
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"Could not connect to FastAPI backend at {FASTAPI_BASE_URL}. Please ensure the backend is running.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"Error fetching question: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

def evaluate_answer(question_id: str, category: str, user_answer: str):
    try:
        payload = {
            "question_id": question_id,
            "category": category,
            "user_answer": user_answer
        }
        response = requests.post(f"{FASTAPI_BASE_URL}/evaluate_answer", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"Could not connect to FastAPI backend at {FASTAPI_BASE_URL}. Please ensure the backend is running.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"Error evaluating answer: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred during evaluation: {e}")
        return None

# --- UI Functions ---
def display_feedback(feedback):
    if feedback:
        st.subheader("💡 Your Feedback")
        st.metric(label="Overall Score", value=f"{feedback['overall_score']:.1f}/100")

        st.markdown(f"**Semantic Similarity:** {feedback['semantic_similarity_score']:.1f}%")
        st.info(feedback['semantic_feedback'])

        st.markdown(f"**Grammar Score:** {feedback['grammar_score']:.1f}%")
        st.info(feedback['grammar_feedback'])
        if feedback['raw_grammar_errors']:
            with st.expander("Show detailed grammar issues (Experimental)"):
                for error in feedback['raw_grammar_errors']:
                    st.json(error)

        st.markdown(f"**Sentiment Score:** {feedback['sentiment_score']:.1f}%")
        st.info(feedback['sentiment_feedback'])

        if feedback['suggestions']:
            st.markdown("---")
            st.subheader("✅ Suggestions for Improvement")
            for suggestion in feedback['suggestions']:
                st.markdown(f"- {suggestion}")
    else:
        st.warning("No feedback available yet.")

def start_new_interview_callback():
    """Callback for 'Start New Interview' button."""
    st.session_state.question = None
    st.session_state.user_answer = ""
    st.session_state.feedback = None
    st.session_state.show_ideal_answer = False
    st.session_state.interview_history = []
    # No st.rerun() here, as Streamlit will rerun naturally after the callback.

def get_next_question_flow_callback():
    """Callback for fetching the next question."""
    st.session_state.user_answer = "" # Clear previous answer
    st.session_state.feedback = None
    st.session_state.show_ideal_answer = False
    new_question = get_random_question(st.session_state.interview_category)
    if new_question:
        st.session_state.question = new_question
    else:
        st.warning("Could not fetch a new question. Please check backend connection.")
    # No st.rerun() here, as Streamlit will rerun naturally after the callback.


# --- Streamlit UI Layout ---
st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("🧠 AI Interview Coach")
st.markdown("""
Welcome to your personal interview practice platform!
Answer the questions, and I'll provide automated feedback on your response's relevance, grammar, and tone.
""")

st.sidebar.header("Interview Settings")
category_options = ["HR", "Technical"]
selected_category = st.sidebar.radio(
    "Choose Interview Category:",
    options=category_options,
    index=category_options.index(st.session_state.interview_category),
    key="category_radio"
)

if selected_category != st.session_state.interview_category:
    st.session_state.interview_category = selected_category
    get_next_question_flow_callback() # Load a new question if category changes
    st.rerun() # Explicit rerun needed here to instantly reflect new category's question and clear main area


st.sidebar.button("Start New Interview", on_click=start_new_interview_callback)
st.sidebar.markdown("---")
st.sidebar.header("Interview History")

if not st.session_state.interview_history:
    st.sidebar.info("No questions answered yet.")
else:
    for i, item in enumerate(st.session_state.interview_history):
        q_text = item['question_text']
        # Check if question_object exists and has an ID before creating key
        if 'question_object' in item and 'id' in item['question_object']:
            # Use a more unique key incorporating question_id
            button_key = f"hist_q_{item['question_object']['id']}_{i}"
        else:
            # Fallback for older history entries or if ID is missing
            button_key = f"hist_q_{i}"

        if st.sidebar.button(f"Q{i+1}: {q_text[:30]}...", key=button_key):
            st.session_state.question = item['question_object']
            st.session_state.user_answer = item['user_answer']
            st.session_state.feedback = item['feedback']
            st.session_state.show_ideal_answer = item['show_ideal_answer'] # Restore state
            st.rerun() # Still need rerun here to update the main content based on selected history item


# Main content area
if st.session_state.question is None:
    st.info("Click 'Get New Question' to start your interview practice!")
    if st.button("Get New Question", key="initial_get_question"):
        get_next_question_flow_callback()
        st.rerun() # Explicit rerun needed here to display the first question immediately
else:
    st.subheader(f"Question ({st.session_state.question['category']} - {st.session_state.question['domain'] or 'N/A'}):")
    st.write(f"**{st.session_state.question['text']}**")

    # User input
    user_answer_input = st.text_area(
        "Your Answer:",
        value=st.session_state.user_answer,
        height=200,
        key="user_answer_textarea"
    )
    
    # Update session state on input change
    if user_answer_input != st.session_state.user_answer:
        st.session_state.user_answer = user_answer_input
        st.session_state.feedback = None # Clear feedback if answer changes
        st.session_state.show_ideal_answer = False # Hide ideal answer
        # No rerun needed here, Streamlit will rerun naturally on text_area change

    col1, col2, col3 = st.columns([1,1,1])

    with col1:
        if st.button("Evaluate Answer", type="primary", key="evaluate_btn"):
            if st.session_state.user_answer.strip() == "":
                st.warning("Please enter your answer before evaluating.")
            else:
                with st.spinner("Evaluating your answer..."):
                    feedback_data = evaluate_answer(
                        st.session_state.question['id'],
                        st.session_state.question['category'],
                        st.session_state.user_answer
                    )
                    if feedback_data:
                        st.session_state.feedback = feedback_data
                        # Add to history
                        st.session_state.interview_history.append({
                            'question_id': st.session_state.question['id'],
                            'question_text': st.session_state.question['text'],
                            'question_object': st.session_state.question, # Store full object
                            'user_answer': st.session_state.user_answer,
                            'feedback': st.session_state.feedback,
                            'show_ideal_answer': st.session_state.show_ideal_answer # Store current state
                        })
                        st.rerun() # Rerun to update history in sidebar and display feedback immediately
    with col2:
        if st.button("Get Next Question", key="next_question_btn"):
            get_next_question_flow_callback()
            st.rerun() # Explicit rerun needed here to display the new question immediately

    with col3:
        if st.session_state.question and st.session_state.question['ideal_answer']:
            if st.button("Toggle Ideal Answer", key="toggle_ideal_btn"):
                st.session_state.show_ideal_answer = not st.session_state.show_ideal_answer
                st.rerun() # Explicit rerun needed here to show/hide ideal answer immediately

    if st.session_state.show_ideal_answer and st.session_state.question and st.session_state.question['ideal_answer']:
        st.markdown("---")
        st.subheader("📚 Ideal Answer:")
        st.info(st.session_state.question['ideal_answer'])

    # Display feedback if available
    if st.session_state.feedback:
        st.markdown("---")
        display_feedback(st.session_state.feedback)