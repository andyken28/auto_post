from datetime import datetime
import json
import logging

from app.extensions import db
from database.models import Log

logger = logging.getLogger(__name__)


def log_action(action: str, status: str, account_id: int = None, error_message: str = None, screenshot_path: str = None):
    """Create a DB log entry and commit, and mirror to file logger.

    This is safe to call from other modules; failures are logged but won't
    raise to the caller unless the DB commit itself raises.
    """
    try:
        entry = Log(
            action=action,
            status=status,
            account_id=account_id,
            error_message=error_message,
            screenshot_path=screenshot_path,
            created_at=datetime.utcnow()
        )
        db.session.add(entry)
        db.session.commit()
    except Exception as e:
        logger.exception("Failed to write log to DB: %s", e)

    # Mirror to file logger
    if status and status.lower() in ('error', 'failed'):
        logger.error('%s account=%s error=%s', action, account_id, error_message)
    else:
        logger.info('%s account=%s status=%s', action, account_id, status)


def query_logs(limit: int = 200, **filters):
    """Return recent logs with optional filters: action, status, account_id, q (search in error_message)."""
    q = Log.query
    if 'action' in filters and filters['action']:
        q = q.filter(Log.action.ilike(f"%{filters['action']}%"))
    if 'status' in filters and filters['status']:
        q = q.filter(Log.status == filters['status'])
    if 'account_id' in filters and filters['account_id']:
        q = q.filter(Log.account_id == filters['account_id'])
    if 'q' in filters and filters['q']:
        q = q.filter(Log.error_message.ilike(f"%{filters['q']}%"))
    return q.order_by(Log.created_at.desc()).limit(limit).all()
