from flask import Blueprint, render_template
from flask_login import login_required, current_user

from database.models import FacebookAccount, Post, Log

main = Blueprint("main", __name__)


@main.route("/")
def index():
  # Provide simple dashboard counts when user is authenticated
  stats = None
  if current_user.is_authenticated:
    try:
      accounts = FacebookAccount.query.count()
    except Exception:
      accounts = 0
    try:
      posts_total = Post.query.count()
      posts_pending = Post.query.filter(Post.status != 'success').count()
    except Exception:
      posts_total = posts_pending = 0
    try:
      logs = Log.query.order_by(Log.created_at.desc()).limit(5).all()
      logs_count = Log.query.count()
    except Exception:
      logs = []
      logs_count = 0

    stats = {
      'accounts': accounts,
      'posts_total': posts_total,
      'posts_pending': posts_pending,
      'logs_count': logs_count,
      'recent_logs': logs,
    }

  return render_template('home.html', stats=stats)


@main.route("/admin")
@login_required
def admin():
  return render_template('admin_stub.html')
