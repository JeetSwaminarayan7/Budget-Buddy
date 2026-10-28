FROM python:3.12-slim

# No .pyc files, and logs go straight to stdout so `docker logs` shows them
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first. This layer only rebuilds when
# requirements.txt changes, not on every code edit.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Don't run as root inside the container
RUN useradd --create-home appuser
USER appuser

EXPOSE 5000

# python:slim has no curl, so the health check uses Python itself
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')" || exit 1

# gunicorn instead of Flask's dev server. --preload imports app.py once,
# so init_db() creates the tables once rather than once per worker.
CMD ["gunicorn", "--preload", "--workers", "2", "--bind", "0.0.0.0:5000", "app:app"]
