import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app

from app.extensions import db
from database.models import Post
from app.utils.images import validate_image_file, save_image_file


def list_posts():
    return Post.query.order_by(Post.created_at.desc()).all()


def get_post(post_id: int):
    return Post.query.get(post_id)


def create_post(data: dict, file_storage=None):
    post = Post(
        title=data.get('title'),
        content=data.get('content'),
        scheduled_time=data.get('scheduled_time'),
        account_id=data.get('account_id'),
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
    post.content = data.get('content') or post.content
    post.scheduled_time = data.get('scheduled_time') or post.scheduled_time
    post.account_id = data.get('account_id') or post.account_id
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
