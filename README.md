# Link Tracker (Python / Flask)
URL shortener with custom aliases and click analytics.

## Run locally
    python -m venv venv
    venv\Scripts\activate      # macOS/Linux: source venv/bin/activate
    pip install -r requirements.txt
    pytest -v
    flake8 .
    python app.py              # http://localhost:5000

## Routes
- GET / : dashboard and form
- POST /shorten : create link (url, optional alias)
- GET /<code> : redirect and count click
- GET /api/links : JSON list
- GET /health : health check

## Pipeline
Push -> Lint (flake8) -> Test (pytest) -> Deploy (main only) -> Live site
