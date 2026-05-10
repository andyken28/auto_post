from flask import Blueprint, render_template, request
from flask_login import login_required

from app.services.log_service import query_logs

logs_bp = Blueprint('logs', __name__, template_folder='templates')


@logs_bp.route('/logs')
@login_required
def logs_list():
    action = request.args.get('action')
    status = request.args.get('status')
    account_id = request.args.get('account_id')
    q = request.args.get('q')

    filters = {'action': action, 'status': status, 'account_id': account_id, 'q': q}
    logs = query_logs(200, **filters)
    return render_template('logs.html', logs=logs, filters=filters)
