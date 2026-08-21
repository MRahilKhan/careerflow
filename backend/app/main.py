from collections import Counter, defaultdict, deque
from time import monotonic
import os

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import create_token, current_user, hash_password, verify_password
from .database import get_db
from .models import (
    Application,
    ApplicationEvent,
    Feedback,
    FollowUp,
    Interview,
    User,
)
from .schemas import (
    ApplicationCreate,
    ApplicationEventCreate,
    ApplicationEventOut,
    ApplicationOut,
    ApplicationUpdate,
    DashboardStats,
    FeedbackCreate,
    FeedbackOut,
    FollowUpCreate,
    FollowUpOut,
    InterviewCreate,
    InterviewOut,
    Login,
    Token,
    UserCreate,
    UserOut,
)


app = FastAPI(
    title="CareerFlow API",
    version="2.0.0",
)


# ============================================================
# CORS
# ============================================================

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CAREERFLOW_ALLOWED_ORIGINS",
        "http://localhost:5173,https://careerflow-liart.vercel.app",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
    ],
)


# ============================================================
# VALIDATION ERRORS
# ============================================================

@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
):
    first = exc.errors()[0]

    location = first.get("loc", [])
    field = location[-1] if location else ""

    messages = {
        "email": "Please enter a valid email address.",
        "password": (
            "Use at least 8 characters with uppercase, lowercase, "
            "a number, and a symbol."
        ),
        "name": "Please enter your name.",
        "job_url": "Please enter a valid HTTP or HTTPS job URL.",
        "meeting_url": "Please enter a valid HTTP or HTTPS meeting URL.",
    }

    return JSONResponse(
        status_code=422,
        content={
            "detail": messages.get(
                field,
                "Please check the highlighted fields and try again.",
            )
        },
    )


# ============================================================
# LOGIN RATE LIMITING
# ============================================================

LOGIN_WINDOW_SECONDS = 15 * 60
LOGIN_MAX_ATTEMPTS = 5

login_attempts: dict[str, deque[float]] = defaultdict(deque)
login_blocks: dict[str, tuple[float, int]] = {}


def get_client_ip(request: Request) -> str:
    """
    Return the client address visible to the application.

    Forwarded headers are intentionally not trusted here because
    they can be spoofed unless they are validated by a trusted proxy.
    """

    if request.client:
        return request.client.host

    return "unknown"


def check_login_allowed(request: Request) -> str:
    client_ip = get_client_ip(request)
    now = monotonic()

    block = login_blocks.get(client_ip)

    if block and block[0] > now:
        remaining = max(
            1,
            int(block[0] - now),
        )

        raise HTTPException(
            status_code=429,
            detail=(
                "Too many login attempts. "
                f"Try again in {remaining} seconds."
            ),
        )

    attempts = login_attempts[client_ip]

    while attempts and now - attempts[0] > LOGIN_WINDOW_SECONDS:
        attempts.popleft()

    return client_ip


def record_failed_login(client_ip: str) -> None:
    attempts = login_attempts[client_ip]

    attempts.append(monotonic())

    if len(attempts) >= LOGIN_MAX_ATTEMPTS:
        previous_strikes = login_blocks.get(
            client_ip,
            (0, 0),
        )[1]

        strike = previous_strikes + 1

        duration = 30 if strike == 1 else 120

        login_blocks[client_ip] = (
            monotonic() + duration,
            strike,
        )

        attempts.clear()


# ============================================================
# BASIC ENDPOINTS
# ============================================================

@app.get("/")
def api_root():
    return {
        "service": "CareerFlow API",
        "status": "healthy",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


# ============================================================
# AUTH
# ============================================================

@app.post(
    "/auth/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: UserCreate,
    db: Session = Depends(get_db),
):
    email = str(payload.email).strip().lower()

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists",
        )

    user = User(
        name=payload.name.strip(),
        email=email,
        password_hash=hash_password(payload.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return Token(
        access_token=create_token(user.id),
    )


@app.post(
    "/auth/login",
    response_model=Token,
)
def login(
    payload: Login,
    request: Request,
    db: Session = Depends(get_db),
):
    client_ip = check_login_allowed(request)

    email = str(payload.email).strip().lower()

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if not user or not verify_password(
        payload.password,
        user.password_hash,
    ):
        record_failed_login(client_ip)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    login_attempts.pop(
        client_ip,
        None,
    )

    login_blocks.pop(
        client_ip,
        None,
    )

    return Token(
        access_token=create_token(user.id),
    )


@app.get(
    "/auth/me",
    response_model=UserOut,
)
def get_me(
    user: User = Depends(current_user),
):
    return user


# ============================================================
# APPLICATIONS
# ============================================================

@app.get(
    "/applications",
    response_model=list[ApplicationOut],
)
def list_applications(
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    query = select(Application).where(
        Application.user_id == user.id
    )

    if status_filter:
        query = query.where(
            Application.status == status_filter
        )

    query = query.order_by(
        Application.applied_at.desc()
    )

    return db.scalars(query).all()


@app.post(
    "/applications",
    response_model=ApplicationOut,
    status_code=status.HTTP_201_CREATED,
)
def create_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    application_data = payload.model_dump()

    if application_data.get("job_url") is not None:
        application_data["job_url"] = str(
            application_data["job_url"]
        )

    item = Application(
        **application_data,
        user_id=user.id,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    event = ApplicationEvent(
        application_id=item.id,
        event_type="status_change",
        title=f"Application created with status: {item.status}",
    )

    db.add(event)
    db.commit()

    return item


@app.put(
    "/applications/{application_id}",
    response_model=ApplicationOut,
)
def update_application(
    application_id: int,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    item = db.scalar(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == user.id,
        )
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    updates = payload.model_dump(
        exclude_unset=True
    )

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one field to update",
        )

    old_status = item.status

    if updates.get("job_url") is not None:
        updates["job_url"] = str(
            updates["job_url"]
        )

    for key, value in updates.items():
        setattr(item, key, value)

    if (
        "status" in updates
        and updates["status"] != old_status
    ):
        event = ApplicationEvent(
            application_id=item.id,
            event_type="status_change",
            title=(
                f"Status changed from {old_status} "
                f"to {item.status}"
            ),
        )

        db.add(event)

    db.commit()
    db.refresh(item)

    return item


@app.delete(
    "/applications/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    item = db.scalar(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == user.id,
        )
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    db.delete(item)
    db.commit()


# ============================================================
# APPLICATION EVENTS
# ============================================================

@app.get(
    "/applications/{application_id}/events",
    response_model=list[ApplicationEventOut],
)
def list_application_events(
    application_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    application = db.scalar(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == user.id,
        )
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    query = (
        select(ApplicationEvent)
        .where(
            ApplicationEvent.application_id == application_id
        )
        .order_by(
            ApplicationEvent.created_at.asc()
        )
    )

    return db.scalars(query).all()


@app.post(
    "/applications/{application_id}/events",
    response_model=ApplicationEventOut,
    status_code=status.HTTP_201_CREATED,
)
def create_application_event(
    application_id: int,
    payload: ApplicationEventCreate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    application = db.scalar(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == user.id,
        )
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    event = ApplicationEvent(
        application_id=application.id,
        event_type=payload.event_type,
        title=payload.title,
        description=payload.description,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


# ============================================================
# INTERVIEWS
# ============================================================

@app.get(
    "/applications/{application_id}/interviews",
    response_model=list[InterviewOut],
)
def list_interviews(
    application_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    application = db.scalar(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == user.id,
        )
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    query = (
        select(Interview)
        .where(
            Interview.application_id == application_id
        )
        .order_by(
            Interview.scheduled_at.asc()
        )
    )

    return db.scalars(query).all()


@app.post(
    "/applications/{application_id}/interviews",
    response_model=InterviewOut,
    status_code=status.HTTP_201_CREATED,
)
def create_interview(
    application_id: int,
    payload: InterviewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    application = db.scalar(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == user.id,
        )
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    interview_data = payload.model_dump()

    if interview_data.get("meeting_url") is not None:
        interview_data["meeting_url"] = str(
            interview_data["meeting_url"]
        )

    interview = Interview(
        application_id=application.id,
        **interview_data,
    )

    db.add(interview)
    db.commit()
    db.refresh(interview)

    event = ApplicationEvent(
        application_id=application.id,
        event_type="interview",
        title=(
            f"Interview scheduled: "
            f"{interview.interview_type}"
        ),
    )

    db.add(event)
    db.commit()

    return interview


# ============================================================
# FOLLOW-UPS
# ============================================================

@app.get(
    "/applications/{application_id}/follow-ups",
    response_model=list[FollowUpOut],
)
def list_follow_ups(
    application_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    application = db.scalar(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == user.id,
        )
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    query = (
        select(FollowUp)
        .where(
            FollowUp.application_id == application_id
        )
        .order_by(
            FollowUp.scheduled_for.asc()
        )
    )

    return db.scalars(query).all()


@app.post(
    "/applications/{application_id}/follow-ups",
    response_model=FollowUpOut,
    status_code=status.HTTP_201_CREATED,
)
def create_follow_up(
    application_id: int,
    payload: FollowUpCreate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    application = db.scalar(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == user.id,
        )
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    follow_up = FollowUp(
        application_id=application.id,
        scheduled_for=payload.scheduled_for,
        note=payload.note,
        status=payload.status,
    )

    db.add(follow_up)
    db.commit()
    db.refresh(follow_up)

    event = ApplicationEvent(
        application_id=application.id,
        event_type="follow_up",
        title="Follow-up scheduled",
        description=payload.note,
    )

    db.add(event)
    db.commit()

    return follow_up


# ============================================================
# FEEDBACK
# ============================================================

@app.post(
    "/feedback",
    response_model=FeedbackOut,
    status_code=status.HTTP_201_CREATED,
)
def create_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    feedback = Feedback(
        **payload.model_dump(),
        user_id=user.id,
    )

    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return feedback


# ============================================================
# DASHBOARD
# ============================================================

@app.get(
    "/dashboard",
    response_model=DashboardStats,
)
def dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    items = db.scalars(
        select(Application).where(
            Application.user_id == user.id
        )
    ).all()

    pipeline = Counter(
        item.status
        for item in items
    )

    responded = (
        pipeline["Interviewing"]
        + pipeline["Offer"]
        + pipeline["Rejected"]
    )

    response_rate = (
        round(
            (responded / len(items)) * 100
        )
        if items
        else 0
    )

    return DashboardStats(
        total=len(items),
        interviewing=pipeline["Interviewing"],
        offers=pipeline["Offer"],
        response_rate=response_rate,
        pipeline=dict(pipeline),
    )
