from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    field_validator,
)


# ============================================================
# AUTH
# ============================================================

class UserCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=80,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=72,
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if len(value) < 2:
            raise ValueError("Name must contain at least 2 characters")

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not any(c.islower() for c in value):
            raise ValueError(
                "Password must contain a lowercase letter"
            )

        if not any(c.isupper() for c in value):
            raise ValueError(
                "Password must contain an uppercase letter"
            )

        if not any(c.isdigit() for c in value):
            raise ValueError(
                "Password must contain a number"
            )

        if not any(not c.isalnum() for c in value):
            raise ValueError(
                "Password must contain a special character"
            )

        return value


class Login(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=1,
        max_length=72,
    )


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    name: str
    email: EmailStr


# ============================================================
# APPLICATIONS
# ============================================================

class ApplicationBase(BaseModel):
    company: str = Field(
        min_length=2,
        max_length=120,
    )

    role: str = Field(
        min_length=2,
        max_length=120,
    )

    location: str = Field(
        default="Remote",
        max_length=120,
    )

    employment_type: str = Field(
        default="Full-time",
        pattern=r"^(Full-time|Part-time|Contract|Internship|Freelance)$",
    )

    work_mode: str = Field(
        default="Unknown",
        pattern=r"^(Remote|Hybrid|Onsite|Unknown)$",
    )

    salary: str | None = Field(
        default=None,
        max_length=80,
    )

    priority: str = Field(
        default="Normal",
        pattern=r"^(Low|Normal|High)$",
    )

    next_step: str | None = Field(
        default=None,
        max_length=180,
    )

    job_url: HttpUrl | None = Field(
        default=None,
    )

    source: str = Field(
        default="Manual",
        min_length=1,
        max_length=80,
    )

    status: str = Field(
        default="Applied",
        pattern=r"^(Wishlist|Applied|Interviewing|Offer|Rejected)$",
    )

    notes: str | None = Field(
        default=None,
        max_length=1500,
    )

    @field_validator(
        "company",
        "role",
        "location",
        "source",
    )
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty")

        return value


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    company: str | None = Field(
        default=None,
        min_length=2,
        max_length=120,
    )

    role: str | None = Field(
        default=None,
        min_length=2,
        max_length=120,
    )

    location: str | None = Field(
        default=None,
        max_length=120,
    )

    employment_type: str | None = Field(
        default=None,
        pattern=r"^(Full-time|Part-time|Contract|Internship|Freelance)$",
    )

    work_mode: str | None = Field(
        default=None,
        pattern=r"^(Remote|Hybrid|Onsite|Unknown)$",
    )

    salary: str | None = Field(
        default=None,
        max_length=80,
    )

    priority: str | None = Field(
        default=None,
        pattern=r"^(Low|Normal|High)$",
    )

    next_step: str | None = Field(
        default=None,
        max_length=180,
    )

    job_url: HttpUrl | None = Field(
        default=None,
    )

    source: str | None = Field(
        default=None,
        min_length=1,
        max_length=80,
    )

    status: str | None = Field(
        default=None,
        pattern=r"^(Wishlist|Applied|Interviewing|Offer|Rejected)$",
    )

    notes: str | None = Field(
        default=None,
        max_length=1500,
    )


class ApplicationOut(ApplicationBase):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    applied_at: datetime


# ============================================================
# APPLICATION EVENTS
# ============================================================

class ApplicationEventCreate(BaseModel):
    event_type: str = Field(
        min_length=2,
        max_length=40,
    )

    title: str = Field(
        min_length=2,
        max_length=160,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )


class ApplicationEventOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    application_id: int
    event_type: str
    title: str
    description: str | None
    created_at: datetime


# ============================================================
# INTERVIEWS
# ============================================================

class InterviewCreate(BaseModel):
    interview_type: str = Field(
        min_length=2,
        max_length=60,
    )

    scheduled_at: datetime

    duration_minutes: int | None = Field(
        default=None,
        ge=1,
        le=480,
    )

    interviewer: str | None = Field(
        default=None,
        max_length=160,
    )

    meeting_url: HttpUrl | None = Field(
        default=None,
    )

    notes: str | None = Field(
        default=None,
        max_length=2000,
    )

    status: str = Field(
        default="Scheduled",
        pattern=r"^(Scheduled|Completed|Cancelled|Rescheduled)$",
    )


class InterviewOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    application_id: int
    interview_type: str
    scheduled_at: datetime
    duration_minutes: int | None
    interviewer: str | None
    meeting_url: HttpUrl | None
    notes: str | None
    status: str


# ============================================================
# FOLLOW-UPS
# ============================================================

class FollowUpCreate(BaseModel):
    scheduled_for: datetime

    note: str = Field(
        min_length=2,
        max_length=500,
    )

    status: str = Field(
        default="Pending",
        pattern=r"^(Pending|Completed|Cancelled)$",
    )


class FollowUpOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    application_id: int
    scheduled_for: datetime
    completed_at: datetime | None
    note: str
    status: str


# ============================================================
# DASHBOARD
# ============================================================

class DashboardStats(BaseModel):
    total: int
    interviewing: int
    offers: int
    response_rate: int
    pipeline: dict[str, int]


# ============================================================
# FEEDBACK
# ============================================================

class FeedbackCreate(BaseModel):
    subject: str = Field(
        min_length=3,
        max_length=120,
    )

    message: str = Field(
        min_length=10,
        max_length=2000,
    )


class FeedbackOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    subject: str
    message: str
    created_at: datetime
