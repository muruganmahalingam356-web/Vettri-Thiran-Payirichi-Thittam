# PocketSmart AI

GenAI-powered budget and recommendation assistant for Home, Party and Jewelry planning.

## Stack
- FastAPI + Jinja2
- SQLite + SQLAlchemy
- Google Gemini via `google-genai`
- JWT authentication
- HTML/CSS/JavaScript frontend

## 1. Setup

```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set:
```env
GEMINI_API_KEY=your_key
SECRET_KEY=replace_with_a_long_random_secret
GEMINI_MODEL=gemini-1.5-flash
```

If your Google account no longer exposes `gemini-1.5-flash`, change `GEMINI_MODEL` to a currently available Gemini model without changing the application code.

## 2. Run

```bash
uvicorn app:app --reload
```

Open http://127.0.0.1:8000

## Project structure

```text
PocketSmartAI/
├── app.py
├── config.py
├── database.py
├── auth.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── models/
│   ├── __init__.py
│   ├── db_models.py
│   └── schemas.py
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py
│   ├── planner_routes.py
│   ├── session_routes.py
│   └── history_routes.py
├── services/
│   ├── __init__.py
│   ├── gemini_utils.py
│   └── recommendation_service.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── home_planner.html
│   ├── party_planner.html
│   ├── jewelry_planner.html
│   ├── recommendations.html
│   └── history.html
└── static/
    ├── styles.css
    ├── app.js
    └── uploads/
```

## Notes
The document describes Amazon, Flipkart, IKEA, Swiggy, Zomato and OYO as sources. This starter project uses generated/search links rather than pretending to have private third-party APIs. Replace the provider-link helpers with official APIs or approved affiliate/search integrations if you later obtain access.
