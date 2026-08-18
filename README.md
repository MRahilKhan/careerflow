# CareerFlow

A focused workspace for managing a modern job search. CareerFlow keeps applications, follow-ups, compensation, work mode, and pipeline health in one place. A companion Chrome extension captures job details directly from listings and application forms.

## Highlights

- Personal account registration and JWT login
- Create, update, filter and delete job applications
- Dashboard metrics and visual pipeline insights
- A responsive, editorial-style React interface
- Python REST API with validation and protected routes
- Chrome extension for one-click and automatic job capture
- Salary, employment type, work mode, priority, next action, and source tracking

## Project structure

- `backend` — FastAPI, SQLAlchemy, SQLite, JWT auth, and protected application routes
- `frontend` — React/Vite dashboard for reviewing and managing the pipeline
- `extension` — Chrome Manifest V3 capture tool for job listings

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

## Browser extension

Open `chrome://extensions`, enable Developer mode, choose **Load unpacked**, and select the `extension` folder. Start the API before using the extension, then connect it with the same CareerFlow account. The extension stores a short-lived access token in Chrome extension storage and never stores the account password.

## Configuration

Copy `backend/.env.example` to `backend/.env` and set a persistent `CAREERFLOW_SECRET_KEY` before deploying. For a hosted frontend, copy `frontend/.env.example` and set `VITE_API_URL` to the public API URL. Use HTTPS and secure cookie-based sessions for a production deployment.
