from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required
from werkzeug.datastructures import FileStorage

from app.services.post_service import list_posts, create_post, get_post, duplicate_post, retry_post, delete_post, update_post
from app.services.facebook_service import list_accounts

posts_bp = Blueprint('posts', __name__, template_folder='templates')


@posts_bp.route('/posts')
@login_required
def posts_list():
    posts = list_posts()
    accounts = list_accounts()
    return render_template('posts.html', posts=posts, accounts=accounts)


@posts_bp.route('/posts/create', methods=['POST'])
@login_required
def posts_create():
    data = request.form.to_dict()
    file = request.files.get('image')
    try:
        create_post(data, file if isinstance(file, FileStorage) else None)
        flash('Post created', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('posts.posts_list'))


@posts_bp.route('/posts/<int:pid>/duplicate', methods=['POST'])
@login_required
def posts_duplicate(pid):
    dup = duplicate_post(pid)
    if dup:
        flash('Post duplicated', 'success')
    else:
        flash('Post not found', 'warning')
    return redirect(url_for('posts.posts_list'))


@posts_bp.route('/posts/<int:pid>/retry', methods=['POST'])
@login_required
def posts_retry(pid):
    p = retry_post(pid)
    if p:
        flash('Retry scheduled', 'success')
    else:
        flash('Post not found', 'warning')
    return redirect(url_for('posts.posts_list'))


@posts_bp.route('/posts/<int:pid>/delete', methods=['POST'])
@login_required
def posts_delete(pid):
    p = get_post(pid)
    if not p:
        return jsonify(error='not found'), 404
    delete_post(p)
    return jsonify(success=True)


@posts_bp.route('/posts/<int:pid>/preview')
@login_required
def posts_preview(pid):
    p = get_post(pid)
    if not p:
        return jsonify(error='not found'), 404
    # return fragment for modal
    return render_template('post_preview_content.html', post=p)
