# Todo Application - SDET Assignment
## This is a full-stack Todo application built with a Next.js frontend and a FastAPI backend.
It provides a simple and intuitive interface for managing your daily tasks with AI-powered summaries.

# Features
Create, Read, Update, Delete (CRUD) operations for todos

AI-Powered Daily Summary: Get a quick overview of tasks that are due today, upcoming, or overdue

Responsive Design: Clean and modern user interface that works on all screen sizes

Load Testing: Pre-configured Locust load test suite to simulate user traffic

Technology Stack
Frontend: Next.js, React, TypeScript, Tailwind CSS

Backend: FastAPI, SQLAlchemy, SQLite

AI: OpenAI API integration

Testing: Jest & Cypress (Frontend), pytest (Backend), Locust (Load Testing)

assignment/
├── backend/
│   ├── tests/              # Backend test files
│   ├── venv/               # Python virtual environment
│   ├── main.py             # FastAPI application
│   ├── .env                # Environment variables
│   ├── requirements.txt    # Python dependencies
│   └── test.db             # SQLite database
└── frontend/
    ├── src/
    │   ├── app/            # Next.js app directory
    │   └── components/     # React components
    ├── cypress/            # E2E tests
    └── package.json        # Node.js dependencies


## 1. Backend Setup
    Navigate to the backend directory:
```bash
    cd backend
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
```

## 2. Frontend Setup
    Navigate to the frontend directory:
```bash
    cd frontend
    Install Node.js dependencies:
    bash
    npm install
```
# Running the Application
## 1. Start the Backend Server
Open a terminal, navigate to the backend directory, and run:

```bash
cd backend
venv\Scripts\activate  # Activate virtual environment on Windows
uvicorn main:app --reload
```
The backend API will be available at http://localhost:8000

## 2. Start the Frontend Application
    Open another terminal, navigate to the frontend directory, and run:

```bash
cd frontend
npm run dev
```

The frontend application will be running at http://localhost:3000

# Running Tests
## Backend Tests
    Navigate to the backend directory and open command line and run:


# API Documentation
## Once the backend is running, you can access the interactive API documentation at:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc


```bash
cd backend
venv\Scripts\activate  # Activate virtual environment
pytest

```


