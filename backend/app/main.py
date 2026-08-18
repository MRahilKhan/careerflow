from collections import Counter, defaultdict, deque
from time import monotonic
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, select, text
from sqlalchemy.orm import Session
from .auth import create_token, current_user, hash_password, verify_password
from .database import Base, engine, get_db
from .models import Application, User
from .schemas import ApplicationCreate, ApplicationOut, ApplicationUpdate, DashboardStats, Login, Token, UserCreate, UserOut

Base.metadata.create_all(bind=engine)

# Keep existing local SQLite databases usable when the workspace gains new fields.
def ensure_application_columns():
    existing = {column["name"] for column in inspect(engine).get_columns("applications")}
    additions = {
        "employment_type": "VARCHAR(30) DEFAULT 'Full-time'",
        "work_mode": "VARCHAR(20) DEFAULT 'Unknown'",
        "salary": "VARCHAR(80)",
        "priority": "VARCHAR(20) DEFAULT 'Normal'",
        "next_step": "VARCHAR(180)",
        "job_url": "VARCHAR(500)",
        "source": "VARCHAR(80) DEFAULT 'Manual'",
    }
    with engine.begin() as connection:
        for name, definition in additions.items():
            if name not in existing:
                connection.execute(text(f"ALTER TABLE applications ADD COLUMN {name} {definition}"))

ensure_application_columns()
app = FastAPI(title="CareerFlow API", version="1.0.0")

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Return calm, user-facing validation copy instead of framework internals."""
    first = exc.errors()[0]
    field = first.get("loc", [""])[-1]
    messages = {
        "email": "Please enter a valid email address.",
        "password": "Use at least 8 characters with uppercase, lowercase, a number, and a symbol.",
        "name": "Please enter your name.",
    }
    return JSONResponse(status_code=422, content={"detail": messages.get(field, "Please check the highlighted fields and try again.")})

app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_origin_regex=r"chrome-extension://.*", allow_credentials=True, allow_methods=["GET", "POST", "PUT", "DELETE"], allow_headers=["Authorization", "Content-Type"])

LOGIN_WINDOW_SECONDS = 15 * 60
LOGIN_MAX_ATTEMPTS = 5
login_attempts: dict[str, deque[float]] = defaultdict(deque)
login_blocks: dict[str, tuple[float, int]] = {}

def check_login_allowed(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    now = monotonic()
    block = login_blocks.get(client_ip)
    if block and block[0] > now:
        remaining = max(1, int(block[0] - now))
        raise HTTPException(429, f"Too many login attempts. Try again in {remaining} seconds.")
    attempts = login_attempts[client_ip]
    while attempts and now - attempts[0] > LOGIN_WINDOW_SECONDS:
        attempts.popleft()
    return client_ip

def record_failed_login(client_ip: str):
    attempts = login_attempts[client_ip]
    attempts.append(monotonic())
    if len(attempts) >= LOGIN_MAX_ATTEMPTS:
        previous_strikes = login_blocks.get(client_ip, (0, 0))[1]
        strike = previous_strikes + 1
        duration = 30 if strike == 1 else 120
        login_blocks[client_ip] = (monotonic() + duration, strike)
        attempts.clear()

@app.get("/health")
def health(): return {"status": "healthy"}

@app.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(409, "An account with this email already exists")
    user = User(name=payload.name, email=payload.email, password_hash=hash_password(payload.password))
    db.add(user); db.commit(); db.refresh(user)
    return Token(access_token=create_token(user.id))

@app.post("/auth/login", response_model=Token)
def login(payload: Login, request: Request, db: Session = Depends(get_db)):
    client_ip = check_login_allowed(request)
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        record_failed_login(client_ip)
        raise HTTPException(401, "Invalid email or password")
    login_attempts.pop(client_ip, None)
    login_blocks.pop(client_ip, None)
    return Token(access_token=create_token(user.id))

@app.get("/auth/me", response_model=UserOut)
def get_me(user: User = Depends(current_user)):
    return user

@app.get("/applications", response_model=list[ApplicationOut])
def list_applications(status_filter: str | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    query = select(Application).where(Application.user_id == user.id)
    if status_filter: query = query.where(Application.status == status_filter)
    return db.scalars(query.order_by(Application.applied_at.desc())).all()

@app.post("/applications", response_model=ApplicationOut, status_code=201)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = Application(**payload.model_dump(), user_id=user.id)
    db.add(item); db.commit(); db.refresh(item); return item

@app.put("/applications/{application_id}", response_model=ApplicationOut)
def update_application(application_id: int, payload: ApplicationUpdate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.scalar(select(Application).where(Application.id == application_id, Application.user_id == user.id))
    if not item: raise HTTPException(404, "Application not found")
    for key, value in payload.model_dump().items(): setattr(item, key, value)
    db.commit(); db.refresh(item); return item

@app.delete("/applications/{application_id}", status_code=204)
def delete_application(application_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.scalar(select(Application).where(Application.id == application_id, Application.user_id == user.id))
    if not item: raise HTTPException(404, "Application not found")
    db.delete(item); db.commit()

@app.get("/dashboard", response_model=DashboardStats)
def dashboard(db: Session = Depends(get_db), user: User = Depends(current_user)):
    items = db.scalars(select(Application).where(Application.user_id == user.id)).all()
    pipeline = Counter(i.status for i in items)
    responded = pipeline["Interviewing"] + pipeline["Offer"] + pipeline["Rejected"]
    return DashboardStats(total=len(items), interviewing=pipeline["Interviewing"], offers=pipeline["Offer"], response_rate=round((responded / len(items)) * 100) if items else 0, pipeline=dict(pipeline))
