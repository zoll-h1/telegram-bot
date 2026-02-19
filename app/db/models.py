from __future__ import annotations

from datetime import date, datetime, time, timezone
from typing import Optional

from sqlalchemy import BigInteger, Date, DateTime, Float, ForeignKey, Index, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    timezone_offset_min: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    reminder_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    last_reminder_local_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    workouts: Mapped[list["WorkoutEntry"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class WorkoutEntry(Base):
    __tablename__ = "workout_entries"
    __table_args__ = (Index("ix_workout_entries_user_performed", "telegram_id", "performed_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user_profiles.telegram_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    exercise: Mapped[str] = mapped_column(String(120), nullable=False)
    sets: Mapped[int] = mapped_column(Integer, nullable=False)
    reps: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    volume_kg: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default="0")
    template: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    performed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    user: Mapped[UserProfile] = relationship(back_populates="workouts")
