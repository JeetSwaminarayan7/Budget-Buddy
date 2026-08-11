# Budget Buddy

A full-stack personal finance dashboard that turns raw bank statement PDFs into categorised transactions, budgets, and AI-generated financial insights.

## Features

- **PDF statement import** — upload a bank statement PDF and have transactions extracted and categorised automatically
- **AI-powered insights** — LLM integration (via Groq) analyses transaction data to surface spending patterns and financial insights
- **Interactive dashboard** — income/expense trends, spending breakdowns, and summary cards built with Recharts
- **Budgeting** — set monthly budgets and savings goals per category, tracked against real spending
- **Authentication** — secure user registration/login with Werkzeug password hashing

## Tech Stack

**Frontend:** React (Vite), JavaScript, Recharts, React Router
**Backend:** Python, Flask, Flask-CORS
**Database:** SQLite
**AI:** Groq LLM API, pdfplumber for PDF parsing
**DevOps:** Docker, Docker Compose, Nginx (frontend serving)

## Architecture

```
frontend (React/Vite) → REST API → backend (Flask) → SQLite
                                        ↓
                                  Groq LLM API (insights, PDF parsing support)
```

The frontend is a single-page React app that talks to the Flask backend over a REST API. The backend handles auth, transaction storage, budget logic, and PDF statement parsing, and calls out to Groq's LLM API to generate natural-language financial insights from transaction data.

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- A free [Groq API key](https://console.groq.com)

### Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # then fill in GROQ_API_KEY and SECRET_KEY
python app.py
```

### Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on Vite's default dev server and expects the backend API to be running locally.

### Running with Docker

```bash
docker-compose up --build
```

This spins up both the backend and frontend containers together.

## Environment Variables

See `backend/.env.example` for the required variables:

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | API key for Groq's LLM API, used for AI-generated insights and PDF parsing support |
| `SECRET_KEY` | Flask session secret. **Must** be set to a random value in any non-local environment — the app falls back to a dev-only default if unset, which is not safe for production. |

## Project Structure

```
budget-buddy/
├── backend/
│   ├── app.py              # Flask app, routes, auth, LLM integration
│   ├── database.py         # SQLite schema and connection handling
│   ├── tests.py            # Backend test suite
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/     # Dashboard widgets (charts, summary cards, etc.)
│       ├── context/        # Auth context
│       └── *.jsx           # Page-level components (Dashboard, Login, Transactions, etc.)
└── docker-compose.yml
```

## Notes

This project was built as a personal portfolio project to explore full-stack development with LLM integration for practical, everyday financial insight generation.
