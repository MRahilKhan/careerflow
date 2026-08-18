# CareerFlow

A job application command center. Built with React, FastAPI, SQLAlchemy, SQLite, and JWT authentication.

## Highlights

- Personal account registration and JWT login
- Create, update, filter and delete job applications
- Dashboard metrics and visual pipeline insights
- A responsive, editorial-style React interface
- Python REST API with validation and protected routes

## Run it locally

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The backend API runs on `http://localhost:8000`.
