# Future Trail | Career Navigator

## 1. Project Overview

Career Navigator v2 is a comprehensive web application designed to assist users in their career development journey. It leverages machine learning and artificial intelligence to provide personalized career recommendations and resume feedback. The application is built with a modern tech stack, featuring a Streamlit frontend for an interactive user experience and a FastAPI backend for robust and scalable API services.

## 2. Core Features

The application offers two primary functionalities accessible after user login:

### 2.1. 🎓 Career Predictor

This feature helps users discover potential career paths based on their academic background, skills, and personal preferences.

**How it works:**
-   Users input various details, including:
    -   **Skills:** Programming languages, web frameworks, databases, etc.
    -   **Interests:** Areas like web development, data science, machine learning.
    -   **Academic Profile:** CGPA, project counts, internship experience.
    -   **Preferences:** Preferred work style (e.g., remote, in-office), interest in further studies (Masters), and research.
-   This information is sent to a machine learning model hosted on the backend.
-   The model, a pre-trained scikit-learn classifier (`careermodel.pkl`), predicts the most suitable career path for the user.
-   The application displays the recommended career and provides a curated list of learning resources to help the user get started in that field.

### 2.2. 📄 ATS Resume Evaluator

This tool provides an automated analysis of a user's resume against a specific job role, simulating an Applicant Tracking System (ATS).

**How it works:**
1.  **Resume Upload:** Users upload their resume in either PDF (`.pdf`) or Microsoft Word (`.docx`) format.
2.  **Text Parsing:** The backend extracts the raw text from the uploaded document.
3.  **AI-Powered Evaluation:** The extracted text is sent to the Google Gemini API along with the target job role.
4.  **Results Display:** The application presents a detailed evaluation to the user, which includes:
    -   **ATS Match Score:** A score from 1 to 10 indicating the resume's relevance to the job role.
    -   **Summary:** A brief overview of the candidate's profile as interpreted by the AI.
    -   **Actionable Suggestions:** Concrete recommendations on how to improve the resume to better align with the target role.

## 3. Technical Architecture

The application is built using a decoupled architecture, with a clear separation between the frontend and backend.

### 3.1. Frontend (Streamlit)

-   **Framework:** [Streamlit](https://streamlit.io/)
-   **Key Libraries:**
    -   `streamlit-authenticator`: For user login and registration.
    -   `plotly`: For creating the ATS score gauge chart.
    -   `requests`: For communicating with the backend API.
-   **Responsibilities:**
    -   Rendering the user interface.
    -   Handling user input and authentication.
    -   Making API calls to the backend.
    -   Displaying results to the user.

### 3.2. Backend (FastAPI)

-   **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
-   **Key Libraries:**
    -   `uvicorn`: As the ASGI server.
    -   `scikit-learn`, `pandas`, `joblib`: For the career prediction machine learning model.
    -   `python-multipart`: For handling file uploads.
    -   `google-generativeai`: For interacting with the Gemini API.
    -   `pdfplumber`, `python-docx`: For parsing resume files.
-   **API Endpoints:**
    -   `POST /predict-career/`: Receives user features and returns a career prediction.
    -   `POST /parse-resume/`: Receives a resume file and returns the extracted text.
    -   `POST /ats-score/`: Receives resume text and a job role, and returns an AI-generated evaluation.

### 3.3. Database

-   **Type:** PostgreSQL
-   **Usage:** Stores user credentials (username, hashed password, email, name) for the authentication system. The connection is handled via `psycopg2-binary`.

### 3.4. Artificial Intelligence & Machine Learning

-   **Career Prediction:** A classification model trained with scikit-learn. The model and associated encoders are stored as `.pkl` files.
-   **Resume Evaluation:** The Google Gemini Pro model (`gemini-1.0-pro`) is used for natural language processing to provide the ATS evaluation. Prompts are dynamically generated to guide the AI's response.

## 4. How to Run

1.  **Set up Environment:**
    -   Install dependencies from `requirements.txt`.
    -   Create a `.env` file with your `GEMINI_API_KEY`.
    -   Set up the PostgreSQL database and provide the connection string in Streamlit's secrets configuration.
2.  **Run Backend:** `uvicorn backend:app --reload`
3.  **Run Frontend:** `streamlit run frontend.py`
