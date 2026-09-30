# FitBuddy – AI Fitness Plan Generator

A complete FastAPI + Jinja2 + SQLite application based on the supplied FitBuddy project documentation.

## What is included

- Personalized 7-day workout generation
- Nutrition/recovery tip generation
- Feedback-based plan regeneration
- SQLite persistence with SQLAlchemy
- Jinja2 responsive frontend
- Admin dashboard with login
- FastAPI JSON API
- Interactive `/docs`
- Structured Gemini JSON output with Pydantic
- Mock AI mode for testing without an API key
- Automated tests

## Architecture

```text
Browser / API client
        |
        v
FastAPI routes
   |         |
   v         v
Jinja2    JSON API
   |
   v
AI service layer ---- Google Gemini API
   |
   v
SQLAlchemy ---- SQLite
```

The original documentation describes Gemini 1.5 Pro and Gemini Flash. Those model names are no longer the recommended current implementation. This version uses the current `google-genai` SDK and configurable model IDs. Defaults are set in `.env.example`.

## 1. Install Python

Use Python 3.11 or newer.

Check:

```powershell
python --version
```

## 2. Open the project in VS Code

Open the `FitBuddy` folder.

## 3. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Configure Gemini

Copy `.env.example` to `.env`.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Open `.env` and set:

```env
GEMINI_API_KEY=your_real_key_here
```

Get a Gemini API key from Google AI Studio.

For a no-cost local UI/API smoke test without Gemini, use:

```env
MOCK_AI=true
```

When `MOCK_AI=true`, the application still exercises the FastAPI, validation, database, templates, feedback, and admin flows, but uses deterministic demo output instead of the Gemini API.

## 6. Run

```bash
uvicorn app.main:app --reload
```

Open:

- Home: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- Admin login: http://127.0.0.1:8000/admin
- Health: http://127.0.0.1:8000/health

The SQLite database is created automatically at `data/fitbuddy.db`.

## 7. Admin

The default example password is:

```text
change-me
```

Change `ADMIN_PASSWORD` and `SESSION_SECRET` in `.env` before using the application beyond local development.

## 8. Test without Gemini first

Set:

```env
MOCK_AI=true
```

Run:

```bash
pytest -q
```

You should see all tests pass.

Then start the server:

```bash
uvicorn app.main:app --reload
```

Create a plan in the browser. Submit feedback such as:

```text
Add more cardio and make one day an active recovery day.
```

The updated plan is saved separately from the original plan.

## 9. Test with real Gemini

Set:

```env
MOCK_AI=false
GEMINI_API_KEY=your_real_key
```

Restart Uvicorn.

Then generate a plan from the home page or use `/docs`.

Example API request:

```json
{
  "name": "Arun",
  "user_id": "arun001",
  "age": 21,
  "weight": 65,
  "goal": "muscle gain",
  "intensity": "medium",
  "experience_level": "beginner"
}
```

POST it to:

```text
/api/generate-workout
```

Feedback example:

```json
{
  "user_id": "arun001",
  "feedback": "Add more cardio and include an additional recovery day."
}
```

POST it to:

```text
/api/feedback
```

## 10. Project structure

```text
FitBuddy/
├── app/
│   ├── __init__.py
│   ├── ai_common.py
│   ├── config.py
│   ├── database.py
│   ├── gemini_flash_generator.py
│   ├── gemini_generator.py
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   ├── schemas.py
│   ├── services.py
│   └── updated_plan.py
├── data/
├── static/
│   ├── app.js
│   └── style.css
├── templates/
│   ├── admin_login.html
│   ├── all_users.html
│   ├── base.html
│   ├── error.html
│   ├── index.html
│   └── result.html
├── tests/
│   └── test_app.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Notes

- This project intentionally keeps the source document's core flow: home form → workout + nutrition generation → feedback update → admin view.
- AI output is constrained to a Pydantic schema so the frontend receives predictable 7-day data.
- Fitness recommendations are general wellness guidance, not medical diagnosis or treatment.
- For production deployment, add HTTPS, a proper identity provider/admin authentication, CSRF protection for browser forms, rate limiting, stricter CORS, encrypted secrets, and a production database.
