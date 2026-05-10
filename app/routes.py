from flask import Blueprint, render_template_string

main = Blueprint("main", __name__)

INDEX_HTML = """<!doctype html>
<html>
<head><meta charset="utf-8"><title>Facebook Auto Post - Base</title></head>
<body>
  <h1>Facebook Auto Post — Base Project</h1>
  <p>Ứng dụng chạy bằng Flask + SQLite. Sử dụng `/auth/login` để đăng nhập.</p>
</body>
</html>
"""


@main.route("/")
def index():
    return render_template_string(INDEX_HTML)
