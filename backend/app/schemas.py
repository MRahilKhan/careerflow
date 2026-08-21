from datetime import datetime
from enum import Enum

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, EmailStr, Field, field_validator


class ApplicationStatus(str, Enum):
    WISHLIST = "Wishlist"
    APPLIED = "Applied"
    INTERVIEWING = "Interviewing"
    OFFER = "Offer"
    REJECTED = "Rejected"


class EmploymentType(str, Enum):
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    INTERNSHIP = "Internship"
    FREELANCE = "Freelance"


class WorkMode(str, Enum):
    REMOTE = "Remote"
    HYBRID = "Hybrid"
    ONSITE = "Onsite"
    UNKNOWN = "Unknown"


class Priority(str, Enum):
    LOW = "Low"
    NORMAL = "Normal"
    HIGH = "High"


class InterviewStatus(str, Enum):
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class FollowUpStatus(str, Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if len(value) < 2:
            raise ValueError("Name must contain at least 2 characters")

        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> EmailStr:
        return EmailStr(str(value).strip().lower())

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not any(c.islower() for c in value):
            raise ValueError("Password must include a lowercase letter")

        if not any(c.isupper() for c in value):
            raise ValueError("Password must include an uppercase letter")

        if not any(c.isdigit() for c in value):
            raise ValueError("Password must include a number")

        if not any(not c.isalnum() for c in value):
            raise ValueError("Password must include a special character")

        return value


class Login(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> EmailStr:
        return EmailStr(str(value).strip().lower())


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr


class ApplicationBase(BaseModel):
    company: str = Field(min_length=2, max_length=120)
    role: str = Field(min_length=2, max_length=120)
    location: str = Field(default="Remote", max_length=120)

    employment_type: EmploymentType = EmploymentType.FULL_TIME
    work_mode: WorkMode = WorkMode.UNKNOWN

    salary: str | None = Field(default=None, max_length=80)
    priority: Priority = Priority.NORMAL
    next_step: str | None = Field(default=None, max_length=180)

    job_url: AnyHttpUrl | None = None

    source: str = Field(default="Manual", min_length=1, max_length=80)

    status: ApplicationStatus = ApplicationStatus.APPLIED

    notes: str | None = Field(default=None, max_length=1500)

    @field_validator("company", "role", "location", "source")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    company: str | None = Field(default=None, min_length=2, max_length=120)
    role: str | None = Field(default=None, min_length=2, max_length=120)
    location: str | None = Field(default=None, max_length=120)

    employment_type: EmploymentType | None = None
    work_mode: WorkMode | None = None

    salary: str | None = Field(default=None, max_length=80)
    priority: Priority | None = None
    next_step: str | None = Field(default=None, max_length=180)

    job_url: AnyHttpUrl | None = None

    source: str | None = Field(default=None, min_length=1, max_length=80)

    status: ApplicationStatus | None = None

    notes: str | None = Field(default=None, max_length=1500)

    @field_validator("company", "role", "location", "source")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty")

        return value


class ApplicationOut(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    applied_at: datetime


class ApplicationEventCreate(BaseModel):
    event_type: str = Field(min_length=2, max_length=40)
    title: str = Field(min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=2000)

    @field_validator("event_type", "title")
    @classmethod
    def strip_event_text(cls, value: str) -> str:
        return value.strip()


class ApplicationEventOut(ApplicationEventCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    application_id: int
    created_at: datetime


class InterviewCreate(BaseModel):
    interview_type: str = Field(min_length=2, max_length=60)
    scheduled_at: datetime
    duration_minutes: int | None = Field(default=None, ge=1, le=1440)
    interviewer: str | None = Field(default=None, max_length=160)
    meeting_url: AnyHttpUrl | None = None
    notes: str | None = Field(default=None, max_length=2000)
    status: InterviewStatus = InterviewStatus.SCHEDULED


class InterviewOut(InterviewCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    application_id: int


class FollowUpCreate(BaseModel):
    scheduled_for: datetime
    note: str = Field(min_length=2, max_length=500)
    status: FollowUpStatus = FollowUpStatus.PENDING


class FollowUpOut(FollowUpCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    application_id: int
    completed_at: datetime | None


class DashboardStats(BaseModel):
    total: int
    interviewing: int
    offers: int
    response_rate: int
    pipeline: dict[str, int]


class FeedbackCreate(BaseModel):
    subject: str = Field(min_length=3, max_length=120)
    message: str = Field(min_length=10, max_length=2000)

    @field_validator("subject", "message")
    @classmethod
    def strip_feedback_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty")

        return value


class FeedbackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject: str
    message: str
    created_at: datetime
