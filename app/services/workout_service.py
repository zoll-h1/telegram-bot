from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
import csv
import io
from collections import Counter

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.models import UserProfile, WorkoutEntry


@dataclass(frozen=True)
class WeeklyStats:
    workouts: int
    total_reps: int
    total_volume_kg: float
    top_exercise: str | None
    window_start: datetime
    window_end: datetime


@dataclass(frozen=True)
class PersonalRecord:
    exercise: str
    best_weight_kg: float


@dataclass(frozen=True)
class DueReminder:
    telegram_id: int
    local_date: date


class WorkoutService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def ensure_profile(self, telegram_id: int) -> None:
        async with self._session_factory() as session:
            profile = await session.get(UserProfile, telegram_id)
            if profile is not None:
                return

            session.add(UserProfile(telegram_id=telegram_id))
            await session.commit()

    async def create_workout(
        self,
        telegram_id: int,
        exercise: str,
        sets: int,
        reps: int,
        weight_kg: float | None,
        template: str | None,
        notes: str | None,
    ) -> WorkoutEntry:
        async with self._session_factory() as session:
            profile = await session.get(UserProfile, telegram_id)
            if profile is None:
                profile = UserProfile(telegram_id=telegram_id)
                session.add(profile)

            volume_kg = 0.0 if weight_kg is None else float(sets * reps) * weight_kg

            workout = WorkoutEntry(
                telegram_id=telegram_id,
                exercise=exercise,
                sets=sets,
                reps=reps,
                weight_kg=weight_kg,
                volume_kg=round(volume_kg, 2),
                template=template,
                notes=notes,
            )
            session.add(workout)
            await session.commit()
            await session.refresh(workout)
            return workout

    async def recent_workouts(self, telegram_id: int, limit: int = 10) -> list[WorkoutEntry]:
        async with self._session_factory() as session:
            stmt = (
                select(WorkoutEntry)
                .where(WorkoutEntry.telegram_id == telegram_id)
                .order_by(desc(WorkoutEntry.performed_at), desc(WorkoutEntry.id))
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def delete_last_workout(self, telegram_id: int) -> bool:
        async with self._session_factory() as session:
            stmt = (
                select(WorkoutEntry)
                .where(WorkoutEntry.telegram_id == telegram_id)
                .order_by(desc(WorkoutEntry.performed_at), desc(WorkoutEntry.id))
                .limit(1)
            )
            result = await session.execute(stmt)
            latest = result.scalar_one_or_none()
            if latest is None:
                return False

            await session.delete(latest)
            await session.commit()
            return True

    async def weekly_stats(self, telegram_id: int, now_utc: datetime | None = None) -> WeeklyStats:
        now = now_utc or datetime.now(timezone.utc)
        window_start = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)

        async with self._session_factory() as session:
            stmt = (
                select(WorkoutEntry)
                .where(
                    WorkoutEntry.telegram_id == telegram_id,
                    WorkoutEntry.performed_at >= window_start,
                    WorkoutEntry.performed_at <= now,
                )
                .order_by(desc(WorkoutEntry.performed_at))
            )
            result = await session.execute(stmt)
            workouts = list(result.scalars().all())

        if not workouts:
            return WeeklyStats(
                workouts=0,
                total_reps=0,
                total_volume_kg=0.0,
                top_exercise=None,
                window_start=window_start,
                window_end=now,
            )

        total_reps = sum(item.sets * item.reps for item in workouts)
        total_volume_kg = round(sum(item.volume_kg for item in workouts), 2)

        exercise_counter = Counter(item.exercise for item in workouts)
        top_exercise = exercise_counter.most_common(1)[0][0]

        return WeeklyStats(
            workouts=len(workouts),
            total_reps=total_reps,
            total_volume_kg=total_volume_kg,
            top_exercise=top_exercise,
            window_start=window_start,
            window_end=now,
        )

    async def personal_records(self, telegram_id: int, limit: int = 7) -> list[PersonalRecord]:
        async with self._session_factory() as session:
            stmt = (
                select(
                    WorkoutEntry.exercise,
                    func.max(WorkoutEntry.weight_kg).label("best_weight"),
                )
                .where(
                    WorkoutEntry.telegram_id == telegram_id,
                    WorkoutEntry.weight_kg.is_not(None),
                )
                .group_by(WorkoutEntry.exercise)
                .order_by(desc("best_weight"), WorkoutEntry.exercise)
                .limit(limit)
            )
            result = await session.execute(stmt)
            rows = result.all()

        records: list[PersonalRecord] = []
        for exercise, best_weight in rows:
            if best_weight is None:
                continue
            records.append(PersonalRecord(exercise=exercise, best_weight_kg=float(best_weight)))

        return records

    async def export_csv_bytes(self, telegram_id: int) -> bytes | None:
        async with self._session_factory() as session:
            stmt = (
                select(WorkoutEntry)
                .where(WorkoutEntry.telegram_id == telegram_id)
                .order_by(desc(WorkoutEntry.performed_at), desc(WorkoutEntry.id))
            )
            result = await session.execute(stmt)
            rows = list(result.scalars().all())

        if not rows:
            return None

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            [
                "performed_at_utc",
                "exercise",
                "sets",
                "reps",
                "weight_kg",
                "volume_kg",
                "template",
                "notes",
            ]
        )

        for row in rows:
            performed_at = row.performed_at
            if performed_at.tzinfo is None:
                performed_at = performed_at.replace(tzinfo=timezone.utc)

            writer.writerow(
                [
                    performed_at.astimezone(timezone.utc).isoformat(),
                    row.exercise,
                    row.sets,
                    row.reps,
                    "" if row.weight_kg is None else row.weight_kg,
                    row.volume_kg,
                    row.template or "",
                    row.notes or "",
                ]
            )

        return buffer.getvalue().encode("utf-8")

    async def set_reminder(self, telegram_id: int, offset_minutes: int, reminder_time: time) -> None:
        async with self._session_factory() as session:
            profile = await session.get(UserProfile, telegram_id)
            if profile is None:
                profile = UserProfile(telegram_id=telegram_id)
                session.add(profile)

            profile.timezone_offset_min = offset_minutes
            profile.reminder_time = reminder_time
            profile.last_reminder_local_date = None
            await session.commit()

    async def disable_reminder(self, telegram_id: int) -> bool:
        async with self._session_factory() as session:
            profile = await session.get(UserProfile, telegram_id)
            if profile is None or profile.reminder_time is None:
                return False

            profile.reminder_time = None
            profile.last_reminder_local_date = None
            await session.commit()
            return True

    async def find_due_reminders(self, now_utc: datetime) -> list[DueReminder]:
        if now_utc.tzinfo is None:
            now_utc = now_utc.replace(tzinfo=timezone.utc)

        async with self._session_factory() as session:
            stmt = select(UserProfile).where(UserProfile.reminder_time.is_not(None))
            result = await session.execute(stmt)
            profiles = list(result.scalars().all())

        due: list[DueReminder] = []
        for profile in profiles:
            if profile.reminder_time is None:
                continue

            local_now = now_utc + timedelta(minutes=profile.timezone_offset_min)
            if (
                local_now.hour != profile.reminder_time.hour
                or local_now.minute != profile.reminder_time.minute
            ):
                continue

            local_date = local_now.date()
            if profile.last_reminder_local_date == local_date:
                continue

            due.append(DueReminder(telegram_id=profile.telegram_id, local_date=local_date))

        return due

    async def mark_reminded(self, telegram_id: int, local_date: date) -> None:
        async with self._session_factory() as session:
            profile = await session.get(UserProfile, telegram_id)
            if profile is None:
                return

            profile.last_reminder_local_date = local_date
            await session.commit()
