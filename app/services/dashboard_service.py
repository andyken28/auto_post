from datetime import datetime

from database.models import User, Post, Job, Log
from app.extensions import db


def get_dashboard_stats():
    """Query the database for dashboard statistics.

    Returns a dict with counts and a list of recent logs.
    """
    stats = {}
    stats["total_accounts"] = User.query.count()
    stats["total_posts"] = Post.query.count()
    stats["posts_success"] = Post.query.filter_by(status="success").count()
    stats["posts_failed"] = Post.query.filter_by(status="failed").count()
    stats["jobs_running"] = Job.query.filter_by(status="running").count()

    # Recent logs (most recent 10)
    recent = Log.query.order_by(Log.created_at.desc()).limit(10).all()
    stats["recent_logs"] = [
        {"level": l.level, "message": l.message, "created_at": l.created_at} for l in recent
    ]

    return stats
