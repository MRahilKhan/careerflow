from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    applications: Mapped[list["Application"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    feedback: Mapped[list["Feedback"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)

    company: Mapped[str] = mapped_column(String(120), index=True)
    role: Mapped[str] = mapped_column(String(120))
    location: Mapped[str] = mapped_column(String(120), default="Remote")

    employment_type: Mapped[str] = mapped_column(
        String(30),
        default="Full-time",
    )

    work_mode: Mapped[str] = mapped_column(
        String(20),
        default="Unknown",
    )

    salary: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        default="Normal",
    )

    next_step: Mapped[str | None] = mapped_column(
        String(180),
        nullable=True,
    )

    job_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    source: Mapped[str] = mapped_column(
        String(80),
        default="Manual",
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="Applied",
    )

    applied_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    user: Mapped["User"] = relationship(
        back_populates="applications",
    )

    events: Mapped[list["ApplicationEvent"]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="ApplicationEvent.created_at",
    )

    interviews: Mapped[list["Interview"]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="Interview.scheduled_at",
    )

    follow_ups: Mapped[list["FollowUp"]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="FollowUp.scheduled_for",
    )


class ApplicationEvent(Base):
    __tablename__ = "application_events"

    id: Mapped[int] = mapped_column(primary_key=True)

    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"),
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(40),
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(160),
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True,
    )

    application: Mapped["Application"] = relationship(
        back_populates="events",
    )


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[int] = mapped_column(primary_key=True)

    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"),
        index=True,
    )

    interview_type: Mapped[str] = mapped_column(
        String(60),
    )

    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime,
        index=True,
    )

    duration_minutes: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    interviewer: Mapped[str | None] = mapped_column(
        String(160),
        nullable=True,
    )

    meeting_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="Scheduled",
        index=True,
    )

    application: Mapped["Application"] = relationship(
        back_populates="interviews",
    )


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id: Mapped[int] = mapped_column(primary_key=True)

    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"),
        index=True,
    )

    scheduled_for: Mapped[datetime] = mapped_column(
        DateTime,
        index=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    note: Mapped[str] = mapped_column(
        String(500),
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="Pending",
        index=True,
    )

    application: Mapped["Application"] = relationship(
        back_populates="follow_ups",
    )


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True)

    subject: Mapped[str] = mapped_column(
        String(120),
    )

    message: Mapped[str] = mapped_column(
        Text,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    user: Mapped["User"] = relationship(
        back_populates="feedback",
    )
