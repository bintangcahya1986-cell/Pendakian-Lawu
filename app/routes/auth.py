from flask import (Blueprint, render_template, request,
                   redirect, url_for, session, flash)
from werkzeug.security import check_password_hash
from ..models import User

auth_bp = Blueprint('auth', __name__)


# ──────────────────────────────────────────────────────────────────────────────
# Login / Logout
# ──────────────────────────────────────────────────────────────────────────────

@auth_bp.route('/', methods=['GET'])
def index():
    """Root — redirect based on current session."""
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Already logged in → bounce away
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username dan password wajib diisi.', 'error')
            return render_template('login.html')

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Username atau password salah.', 'error')
            return render_template('login.html')

        if not user.is_active:
            flash('Akun ini sudah dinonaktifkan. Hubungi Admin.', 'error')
            return render_template('login.html')

        # Persist session
        session.permanent = True
        session['user_id']   = user.id
        session['username']  = user.username
        session['full_name'] = user.full_name
        session['role']      = user.role

        flash(f'Selamat datang, {user.full_name}!', 'success')

        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user.dashboard'))

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Kamu telah keluar dari sesi.', 'info')
    return redirect(url_for('auth.login'))
