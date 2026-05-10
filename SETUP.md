Setup Guide — AutoPost (Windows)

1. Create Python virtual environment and activate (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

2. Install Playwright browsers:

```powershell
python -m playwright install
```

3. Configure environment variables (optional):

- `SECRET_KEY` — set a secure secret
- `DATABASE_URL` — override DB location
- `SESSION_COOKIE_SECURE` — `True` for HTTPS
- `ADMIN_PASS` — change default admin password

4. Run the app:

```powershell
python app.py
```

The app runs on port 8080 by default.
