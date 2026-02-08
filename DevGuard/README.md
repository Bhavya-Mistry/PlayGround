# 🛡️ DevGuard: AI-Powered Automated Code Reviewer

**DevGuard** is an intelligent middleware that acts as an automated Senior Software Engineer. It listens to GitHub Pull Requests, analyzes code changes using LLMs (Llama 3 via Groq), detects security vulnerabilities, and provides instant feedback directly on the PR.

![Architecture Status](https://img.shields.io/badge/Status-Live-green)
![Tech Stack](https://img.shields.io/badge/Stack-FastAPI_|_Supabase_|_Groq_|_Render-blue)

## 🚀 Features

* **⚡ Zero-Latency Analysis:** Uses Groq's LPU inference engine for sub-second code reviews.
* **🔒 Bank-Grade Security:** Verifies GitHub Webhook signatures (HMAC SHA-256) to prevent spoofing.
* **🧠 Context-Aware:** Detects SQL Injection, Hardcoded Secrets, and O(n²) performance bottlenecks.
* **💾 Persistent Memory:** Logs all reviews and metadata to a PostgreSQL database (Supabase).
* **📊 Live Dashboard:** Includes a real-time web dashboard to track code quality metrics.

## 🏗️ Architecture

1.  **Trigger:** Developer opens a Pull Request on GitHub.
2.  **Ingest:** GitHub sends a webhook payload to the **FastAPI** backend (hosted on Render).
3.  **Security:** Backend verifies the `X-Hub-Signature-256` to ensure authenticity.
4.  **Analysis:** The `diff` is extracted and sent to **Llama 3.1-8b** via Groq API.
5.  **Response:** The AI's feedback is posted back to the PR as a comment.
6.  **Storage:** The review data is archived in **Supabase** (PostgreSQL).
7.  **Visualization:** The frontend fetches data via a REST API to display analytics.

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI, SQLAlchemy
* **AI Engine:** Groq (Llama 3.1-8b-instant)
* **Database:** PostgreSQL (Supabase)
* **Infrastructure:** Render (Cloud Hosting)
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla)

## 🔧 Setup & Installation

### Prerequisites
* Python 3.10+
* PostgreSQL URL
* Groq API Key
* GitHub Personal Access Token

### Local Development

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/your-username/devguard.git](https://github.com/your-username/devguard.git)
    cd devguard
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables (.env)**
    ```env
    GITHUB_TOKEN=your_github_token
    GROQ_API_KEY=your_groq_key
    DATABASE_URL=your_supabase_url
    GITHUB_WEBHOOK_SECRET=your_secret_key
    ```

4.  **Run the server**
    ```bash
    uvicorn main:app --reload
    ```
