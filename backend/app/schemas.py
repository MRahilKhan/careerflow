from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not all((any(c.islower() for c in value), any(c.isupper() for c in value), any(c.isdigit() for c in value), any(not c.isalnum() for c in value))):
            raise ValueError("Password must include uppercase, lowercase, number, and special character")
        return value

class Login(BaseModel):
    email: EmailStr
    password: str

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
    employment_type: str = Field(default="Full-time", pattern="^(Full-time|Part-time|Contract|Internship|Freelance)$")
    work_mode: str = Field(default="Unknown", pattern="^(Remote|Hybrid|Onsite|Unknown)$")
    salary: str | None = Field(default=None, max_length=80)
    priority: str = Field(default="Normal", pattern="^(Low|Normal|High)$")
    next_step: str | None = Field(default=None, max_length=180)
    job_url: str | None = Field(default=None, max_length=500)
    source: str = Field(default="Manual", max_length=80)
    status: str = Field(default="Applied", pattern="^(Wishlist|Applied|Interviewing|Offer|Rejected)$")
    notes: str | None = Field(default=None, max_length=1500)

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(ApplicationBase):
    pass

class ApplicationOut(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    applied_at: datetime

class DashboardStats(BaseModel):
    total: int
    interviewing: int
    offers: int
    response_rate: int
    pipeline: dict[str, int]
