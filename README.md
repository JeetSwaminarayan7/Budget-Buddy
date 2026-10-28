# Budget Buddy

A full-stack personal finance dashboard that turns raw bank statement PDFs into categorised transactions, budgets, and AI-generated financial insights.

## Features

- **PDF statement import** — upload a bank statement PDF and have transactions extracted and categorised automatically
- **AI-powered insights** — LLM integration (via Groq) analyses transaction data to surface spending patterns and financial insights
- **Interactive dashboard** — income/expense trends, spending breakdowns, and summary cards built with Recharts
- **Budgeting** — set monthly budgets and savings goals per category, tracked against real spending
- **Authentication** — secure user registration/login with Werkzeug password hashing

## Tech Stack

**Frontend:** React (Vite), TypeScript, Recharts, React Router
**Backend:** Python, Flask, Flask-CORS
**Database:** PostgreSQL 16
**AI:** Groq LLM API, pdfplumber for PDF parsing
**DevOps:** Docker, Docker Compose, Kubernetes (kind), Nginx, GitHub Actions CI

## Architecture

```
frontend (React/Vite) → REST API → backend (Flask) → PostgreSQL
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

### Running with Docker Compose

You need Docker Desktop (or Docker Engine with the compose plugin).

```bash
cp backend/.env.example backend/.env   # optional: add GROQ_API_KEY for PDF upload
docker compose up --build
```

That starts three containers:

| Service | What it is | Port |
|---|---|---|
| `db` | PostgreSQL 16, data kept in the `pgdata` volume | internal only |
| `backend` | Flask API under gunicorn, built from `backend/Dockerfile` | 5000 |
| `frontend` | React build served by nginx, which proxies `/api` to the backend | 80 |

Open http://localhost, or check the API with `curl localhost:5000/api/health`.

The backend creates its tables when it starts, so compose waits for Postgres's health check to pass before starting it. `docker compose down` stops everything and keeps the data; `docker compose down -v` deletes the database too.

The backend image runs as a non-root user, has its own health check, and installs dependencies in a separate layer so code changes don't trigger a full reinstall.

### Running on Kubernetes locally (kind)

[kind](https://kind.sigs.k8s.io/) runs a Kubernetes cluster inside Docker on your own machine. This deploys the backend and Postgres to it.

Install kind and kubectl (macOS with Homebrew shown; see the kind docs for Windows and Linux):

```bash
brew install kind kubectl
```

Create a cluster, then build the backend image and load it into the cluster. kind can't see images on your machine until you load them:

```bash
kind create cluster --name budget-buddy
docker build -t budget-buddy-backend:local ./backend
kind load docker-image budget-buddy-backend:local --name budget-buddy
```

Create the secrets. They're kept out of the repo on purpose:

```bash
kubectl create secret generic budget-buddy-secrets \
  --from-literal=POSTGRES_PASSWORD=budgetpass \
  --from-literal=SECRET_KEY=$(openssl rand -hex 32) \
  --from-literal=GROQ_API_KEY=your_groq_key_here
```

Deploy and wait for it to come up:

```bash
kubectl apply -f k8s/
kubectl rollout status deployment/postgres
kubectl rollout status deployment/backend
kubectl get pods
```

You should see one `postgres` pod and two `backend` pods, all `Running`. Then forward a local port to the backend Service and test it:

```bash
kubectl port-forward service/backend 5000:5000
curl localhost:5000/api/health
```

How it fits together:

- `k8s/postgres.yaml` has a Deployment running one Postgres pod, a PersistentVolumeClaim so the data survives the pod restarting, and a Service that gives it the hostname `postgres` inside the cluster.
- `k8s/backend.yaml` has a Deployment running two copies of the backend and a Service that spreads requests across them. An init container waits for Postgres before the app starts. The readiness probe keeps traffic away from a pod until `/api/health` answers, and the liveness probe restarts a pod that stops answering.
- Passwords and keys come from the `budget-buddy-secrets` Secret, not from the YAML.

Some things to try: `kubectl delete pod <backend-pod>` and watch the Deployment replace it, or `kubectl scale deployment/backend --replicas=3`.

To tear it all down:

```bash
kind delete cluster --name budget-buddy
```

The frontend isn't deployed to the cluster yet. Its nginx config already proxies to a host called `backend`, so it would work as a third Deployment and Service behind the same names.

## Environment Variables

See `backend/.env.example` for the required variables:

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | API key for Groq's LLM API, used for AI-generated insights and PDF parsing support |
| `DATABASE_URL` | PostgreSQL connection string. Compose and the Kubernetes manifests set this for you |
| `SECRET_KEY` | Flask session secret. **Must** be set to a random value in any non-local environment — the app falls back to a dev-only default if unset, which is not safe for production. |

## Project Structure

```
budget-buddy/
├── backend/
│   ├── app.py              # Flask app, routes, auth, LLM integration
│   ├── database.py         # PostgreSQL schema and connection handling
│   ├── Dockerfile
│   ├── tests.py            # Backend test suite
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/     # Dashboard widgets (charts, summary cards, etc.)
│       ├── context/        # Auth context
│       └── *.tsx           # Page-level components (Dashboard, Login, Transactions, etc.)
├── k8s/
│   ├── postgres.yaml       # Postgres Deployment, Service and volume claim
│   └── backend.yaml        # Backend Deployment and Service
└── docker-compose.yml
```

## Notes

This project was built as a personal portfolio project to explore full-stack development with LLM integration for practical, everyday financial insight generation.
