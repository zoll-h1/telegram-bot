# Gym Progress Coach (Telegram Bot)

Portfolio-grade Telegram bot for workout tracking built with `aiogram 3` + `SQLAlchemy`.

## Features

- Structured workout logging flow (template -> exercise -> sets/reps/weight/notes)
- Weekly stats for last 7 days
- Personal records table (max weight per exercise)
- Workout history with inline delete/refresh
- CSV export for all workouts
- Daily reminder system with timezone support (`UTC+/-offset`)

## Stack

- Python 3.11+
- aiogram 3
- SQLAlchemy 2 (async)
- SQLite by default (can switch to PostgreSQL via `DATABASE_URL`)

## Project Structure

```text
app/
  config.py
  main.py
  db/
  handlers/
  keyboards/
  services/
  states/
  utils/
tests/
main.py
```

## Setup

1. Create virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create `.env` from example:

```bash
cp .env.example .env
```

3. Put your **new BotFather token** into `.env` (`BOT_TOKEN=...`).

4. Run bot:

```bash
python main.py
```

## Deploy To Railway

1. Push this repo to GitHub.
2. In Railway, create a new project from this repo.
3. Keep service as a worker/background service (no HTTP port needed).
4. Add environment variables in Railway:
   - `BOT_TOKEN`
   - `DATABASE_URL` (use Railway Postgres URL for persistent data)
   - `LOG_LEVEL`
   - `REMINDER_POLL_SECONDS`
5. Deploy.

This repository includes:

- `railway.json` with `startCommand: python main.py`
- `Procfile` with `worker: python main.py`

## Commands

- `/start` open menu
- `/add` add workout
- `/history` show recent workouts
- `/stats` weekly stats
- `/prs` personal records
- `/export` export CSV
- `/reminder` set reminder
- `/reminder_off` disable reminder
- `/cancel` cancel current flow

## Notes

- Do not reuse your NanoBot production token here.
- Use a separate token for this portfolio bot so NanoBot stays unaffected.
