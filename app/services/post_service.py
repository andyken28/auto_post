import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
import bleach
from sqlalchemy.orm import joinedload

from app.extensions import db
from database.models import Post
from app.utils.images import validate_image_file, save_image_file


def list_posts(page: int = 1, per_page: int = 20, q: str = None, account_id: int = None, status: str = None):
    """Return paginated posts with optional search and filters.

    Returns a dict: {items, total, page, per_page}
    """
    query = Post.query.options(joinedload(Post.account))
    if q:
        query = query.filter(Post.content.ilike(f"%{q}%") | Post.title.ilike(f"%{q}%"))
    if account_id:
        query = query.filter(Post.account_id == account_id)
    if status:
        query = query.filter(Post.status == status)

    total = query.with_entities(db.func.count(Post.id)).scalar() or 0
    items = query.order_by(Post.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return {"items": items, "total": total, "page": page, "per_page": per_page}


def get_post(post_id: int):
    return Post.query.get(post_id)


def create_post(data: dict, file_storage=None):
    # sanitize HTML content
    content = data.get('content') or ''
    allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li']
    allowed_attrs = {'a': ['href', 'title', 'rel', 'target']}
    clean_content = bleach.clean(content, tags=allowed_tags, attributes=allowed_attrs, strip=True)

    scheduled = data.get('scheduled_time')
    sched_dt = None
    if scheduled:
        try:
            sched_dt = datetime.fromisoformat(scheduled)
        except Exception:
            sched_dt = None

    post = Post(
        title=data.get('title'),
        content=clean_content,
        scheduled_time=sched_dt,
        account_id=(int(data.get('account_id')) if data.get('account_id') else None),
        status=data.get('status') or 'pending'
    )

    if file_storage:
        filename = secure_filename(file_storage.filename)
        if validate_image_file(file_storage.stream, filename):
            uploads = current_app.config.get('UPLOAD_FOLDER') or os.path.join(current_app.root_path, '..', 'uploads')
            saved = save_image_file(file_storage, uploads, filename)
            # store relative path
            post.image_path = os.path.relpath(saved, start=current_app.root_path)
        else:
            raise ValueError('Invalid image')

    db.session.add(post)
    db.session.commit()
    return post


def update_post(post: Post, data: dict, file_storage=None):
    post.title = data.get('title') or post.title
    if 'content' in data:
        clean_content = bleach.clean(data.get('content') or '', tags=['b', 'i', 'u', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li'], attributes={'a': ['href', 'title', 'rel', 'target']}, strip=True)
        post.content = clean_content
    if 'scheduled_time' in data and data.get('scheduled_time'):
        try:
            post.scheduled_time = datetime.fromisoformat(data.get('scheduled_time'))
        except Exception:
            pass
    if 'account_id' in data and data.get('account_id'):
        post.account_id = int(data.get('account_id'))
    if file_storage:
        filename = secure_filename(file_storage.filename)
        if validate_image_file(file_storage.stream, filename):
            uploads = current_app.config.get('UPLOAD_FOLDER') or os.path.join(current_app.root_path, '..', 'uploads')
            saved = save_image_file(file_storage, uploads, filename)
            post.image_path = os.path.relpath(saved, start=current_app.root_path)
        else:
            raise ValueError('Invalid image')

    db.session.commit()
    return post


def duplicate_post(post_id: int):
    orig = get_post(post_id)
    if not orig:
        return None
    dup = Post(
        title=(orig.title or '') + ' (copy)',
        content=orig.content,
        image_path=orig.image_path,
        scheduled_time=None,
        account_id=orig.account_id,
        status='pending'
    )
    db.session.add(dup)
    db.session.commit()
    return dup


def retry_post(post_id: int):
    post = get_post(post_id)
    if not post:
        return None
    post.retry_count = (post.retry_count or 0) + 1
    post.status = 'pending'
    post.scheduled_time = datetime.utcnow()
    db.session.commit()
    return post


def delete_post(post: Post):
    db.session.delete(post)
    db.session.commit()
