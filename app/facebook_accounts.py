from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required

from app.services.facebook_service import (
    list_accounts, create_account, get_account, update_account,
    delete_account, toggle_account, test_proxy_for_account, test_login_for_account
)

fb = Blueprint('facebook_accounts', __name__, template_folder='templates')


@fb.route('/accounts')
@login_required
def accounts_list():
    q = request.args.get('q')
    accounts = list_accounts(q)
    return render_template('accounts.html', accounts=accounts, q=q)


@fb.route('/accounts/create', methods=['POST'])
@login_required
def accounts_create():
    data = request.form.to_dict()
    create_account(data)
    flash('Account created', 'success')
    return redirect(url_for('facebook_accounts.accounts_list'))


@fb.route('/accounts/<int:aid>/edit', methods=['POST'])
@login_required
def accounts_edit(aid):
    acc = get_account(aid)
    if not acc:
        flash('Account not found', 'warning')
        return redirect(url_for('facebook_accounts.accounts_list'))
    update_account(acc, request.form.to_dict())
    flash('Account updated', 'success')
    return redirect(url_for('facebook_accounts.accounts_list'))


@fb.route('/accounts/<int:aid>/delete', methods=['POST'])
@login_required
def accounts_delete(aid):
    acc = get_account(aid)
    if not acc:
        return jsonify(error='not found'), 404
    delete_account(acc)
    return jsonify(success=True)


@fb.route('/accounts/<int:aid>/toggle', methods=['POST'])
@login_required
def accounts_toggle(aid):
    acc = get_account(aid)
    enable = request.form.get('enable', '1') in ('1', 'true', 'True')
    toggle_account(acc, enable)
    return jsonify(success=True, status=acc.status)


@fb.route('/accounts/<int:aid>/test-proxy')
@login_required
def accounts_test_proxy(aid):
    acc = get_account(aid)
    ok = test_proxy_for_account(acc)
    return jsonify(ok=ok)


@fb.route('/accounts/<int:aid>/test-login')
@login_required
def accounts_test_login(aid):
    acc = get_account(aid)
    ok = test_login_for_account(acc)
    return jsonify(ok=ok)
