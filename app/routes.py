from flask import Blueprint, render_template_string
from flask_login import login_required, current_user

main = Blueprint("main", __name__)

INDEX_HTML = """<!doctype html>
<html>
<head><meta charset="utf-8"><title>Facebook Auto Post - Base</title></head>
<body>
  <h1>Facebook Auto Post — Base Project</h1>
  <p>Ứng dụng chạy bằng Flask + SQLite. Sử dụng <a href="/auth/login">/auth/login</a> để đăng nhập.</p>
  <p><a href="/admin">Admin area (protected)</a></p>
  {% if current_user.is_authenticated %}
  <p>Đăng nhập dưới tên: {{ current_user.username }} — <a href="/auth/logout">Logout</a></p>
  {% endif %}
</body>
</html>
"""


@main.route("/")
def index():
    return render_template_string(INDEX_HTML)


@main.route("/admin")
@login_required
def admin():
    return render_template_string("<h2>Admin area</h2><p>Chỉ dành cho user đã đăng nhập.</p>")
