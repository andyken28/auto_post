Troubleshooting — AutoPost

Common issues:

- ModuleNotFoundError: No module named 'flask'
  - Ensure virtualenv is activated and `pip install -r requirements.txt` ran in that env.

- Playwright errors or missing browser binaries
  - Run `python -m playwright install`.
  - Ensure the environment has network access for downloads.

- SQLite "database is locked"
  - Avoid multiple simultaneous writers. For production use PostgreSQL.

- CSRF token missing or invalid on AJAX
  - Ensure the client sends header `X-CSRFToken` with the value from `meta[name="csrf-token"]`.

- Permissions when saving uploads/screenshots
  - Ensure the process has write permissions for `uploads/`, `logs/`, `profiles/` and `screenshots/` folders.

If problems persist, enable `DEBUG=True` in `config.py` (development only) and inspect server logs in `logs/`.
