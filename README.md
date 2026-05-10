# AutoPost — Facebook Auto Post (MVP)

This repository is a minimal production-style MVP for automated Facebook posting using Flask, Playwright and an APScheduler-based scheduler.

## Quick start (development / local Windows)

- Create and activate a Python virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

- Install Playwright browsers (required for Playwright automation):

```powershell
python -m playwright install
```

- Initialize database and run app:

```powershell
python app.py
```

Open http://localhost:8080 in your browser.

Default admin user (development): username `admin` password `nm1111` — change this in environment `ADMIN_PASS` in production.

## What's included

- Flask app factory with Blueprints for auth, dashboard, accounts, posts, logs.
- SQLite DB via SQLAlchemy with indexes to improve query performance.
- Playwright-based poster that uses persistent profiles and saves error screenshots.
- APScheduler async scheduler to dispatch scheduled posts.
- CSRF protection (Flask-WTF) and input sanitization (bleach) on user inputs.
- UI improvements: toasts, loading overlay, search, pagination.
- Basic logging: rotating file handlers and DB log table.

## BƯỚC 10 — Final optimizations & security

This step focuses on making the MVP production-friendly for local deployment:

- Hardened session cookie settings (`SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE`, `SESSION_COOKIE_SECURE`).
- CSRF protection enabled through `Flask-WTF` (`CSRFProtect`).
- Input sanitization using `bleach` for HTML fields and account names.
- SQLite optimizations: added indexes on frequently queried columns.
- Pagination, search and filter on the Posts and Accounts views.
- UI helpers: toast notifications and submission loading overlay.

## Setup Guide (Windows)

1. Create and activate venv:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Install Playwright browsers (important):

```powershell
python -m playwright install
```

3. Optional environment variables (for production/local hardening):

- `SECRET_KEY` — set a secure random value.
- `DATABASE_URL` — optional, e.g. `sqlite:///C:/path/to/app.db` or a Postgres URL.
- `SESSION_COOKIE_SECURE` — set to `True` in HTTPS environments.
- `SESSION_COOKIE_SAMESITE` — `Lax` recommended; set to `Strict` for stricter CSRF protection.
- `ADMIN_PASS` — override default admin password.

4. Start the app:

```powershell
python app.py
```

5. Visit `http://localhost:8080`.

## Playwright notes

- Playwright browser binaries are not bundled: run `python -m playwright install` once per environment.
- On Windows with headful mode, Playwright will open Chromium windows; for headless operation in automation, set `headless=True` in `PlaywrightManager.launch_persistent_context()` configuration.

## Troubleshooting

- "ModuleNotFoundError: No module named 'flask'": ensure you activated the virtualenv and installed `requirements.txt` in that environment.
- Playwright errors: run `python -m playwright install` and ensure your Python environment can start Chromium.
- Database locked errors (SQLite): avoid multiple processes writing simultaneously; consider switching to PostgreSQL for concurrency.
- CSRF failures on XHR/fetch: ensure client sends the `X-CSRFToken` header. The app exposes `meta[name="csrf-token"]` in templates and sample fetch code uses it.

## Security notes

- Do not store production secrets in the repository. Use environment variables or a secrets manager.
- Set `SESSION_COOKIE_SECURE=True` when serving over HTTPS.
- Consider running the Playwright automation in a separate worker process or container with limited privileges.

## Development tips

- When updating models that change schema (indexes or new columns), remove the local SQLite DB `database/app.db` during development or migrate using Alembic for production.
- Add `database/app.db`, `logs/` and `profiles/` to `.gitignore` if you do not want these artifacts committed.

---

If you'd like, I can:

- Run a local smoke test seeding a post that triggers a screenshot/log on failure (requires Playwright install).
- Add Alembic migrations for DB schema changes.
- Add a small Dockerfile for local isolation on Windows.

Which of those should I do next?
