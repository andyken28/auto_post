# Facebook Auto Post — Base (Step 1)

Base project that runs locally with Flask + SQLite and basic auth (Flask-Login).

Quick start

1. Create a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Run the app:

```bash
python app.py
```

The app listens on port `8080`. Visit http://localhost:8080

Endpoints

- `/` — index
- `/health` — JSON health check
- `/auth/login` — POST `username` & `password` to login (dev: auto-creates user)
- `/auth/logout` — logout

Project architecture

- `app/` — Flask application package (factory, blueprints, extensions)
- `database/` — SQLAlchemy models
- `logs/` — runtime logs (created automatically)
- `uploads/` — uploaded files
- `profiles/` — saved profiles (future)
- `screenshots/` — screenshots (future)

Files created (Step 1)

- `app.py` — application runner (port 8080)
- `config.py` — configuration classes and SQLite path
- `logger.py` — centralized logging setup
- `requirements.txt` — dependencies
- `README.md` — this file

Next steps

- Implement posting worker and scheduler
- Add full user/profile management UI
- Add tests and CI

# Ứng dụng Python đơn giản

Hướng dẫn nhanh để chạy ứng dụng web trên cổng 8080.

1. Cài phụ thuộc:

```bash
python -m pip install -r requirements.txt
```

2. Chạy ứng dụng:

```bash
python app.py
```

3. Mở trình duyệt vào: http://localhost:8080

Endpoint kiểm tra sức khỏe: http://localhost:8080/health
