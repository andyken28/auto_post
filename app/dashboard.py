from flask import Blueprint, render_template
from flask_login import login_required

from app.services.dashboard_service import get_dashboard_stats

dashboard = Blueprint("dashboard", __name__, template_folder="templates")


@dashboard.route("/")
@login_required
def index():
    stats = get_dashboard_stats()
    return render_template("dashboard.html", stats=stats)
