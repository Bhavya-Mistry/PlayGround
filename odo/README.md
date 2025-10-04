# Expense Management System

A full-stack web application for managing company expense claims with a flexible, multi-level approval workflow.

---

## Features

-   **Role-Based Access Control**: Separate interfaces and permissions for Employees, Managers, and Admins.
-   **Expense Submission**: Employees can submit expense claims with details and receipt uploads.
-   **Multi-Level Approval Workflow**: Admins can define a sequential approval chain (e.g., Manager -> Finance -> Director).
-   **Dynamic Workflows**: Automatically add an employee's direct manager as the first approver.
-   **User Management**: Admins can create and manage all users within their organization.
-   **Secure Authentication**: Uses JWT for secure, token-based authentication.

---

## Tech Stack

-   **Backend**: FastAPI (Python), MongoDB
-   **Frontend**: React, Vite, Tailwind CSS
-   **Containerization**: Docker (for MongoDB)

---

## Prerequisites

Make sure you have the following installed on your system:
-   **Docker** & **Docker Compose**
-   **Python** 3.8+ and `pip`
-   **Node.js** v18+ and `npm`

---

## Setup & Installation

1.  **Clone the repository (or ensure your project folder is ready).**

2.  **Backend Setup:**
    -   Navigate to the `backend` directory: `cd backend`
    -   Create a `.env` file and add the following content:
        ```env
        MONGO_URL="mongodb://admin:password@localhost:27017/"
        MONGO_DB_NAME="expense_management_db"
        SECRET_KEY="your-super-secret-and-long-random-string-for-security"
        ```
    -   Install the required Python packages:
        ```bash
        pip install -r requirements.txt
        ```

3.  **Frontend Setup:**
    -   Navigate to the `frontend` directory: `cd frontend`
    -   Install the required Node.js packages:
        ```bash
        npm install
        ```

---

## Running the Application

You need to have three terminals open to run the full application.

### 1. Start the Database

In your project's root directory (`expense-management/`), start the MongoDB database using Docker.

```bash
docker-compose up -d