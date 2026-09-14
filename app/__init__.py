import os
from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, session, redirect, url_for
from .database import db, init_db

load_dotenv()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # ── Core config ────────────────────────────────────────────
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'sqlite:///' + os.path.join(app.instance_path, 'pendakian.db')
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ── Session security ───────────────────────────────────────
    app.config['SESSION_COOKIE_HTTPONLY'] = True   # JS cannot read cookie
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF mitigation
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    with app.app_context():
        from . import models  # noqa: F401
        db.create_all()
        init_db(app)

    # ── Blueprints ─────────────────────────────────────────────
    from .routes.auth  import auth_bp
    from .routes.admin import admin_bp
    from .routes.user  import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp,  url_prefix='/user')

    # ── Security headers (every response) ─────────────────────
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options']        = 'DENY'
        response.headers['X-XSS-Protection']       = '1; mode=block'
        response.headers['Referrer-Policy']         = 'strict-origin-when-cross-origin'
        return response

    # ── Session expiry guard ───────────────────────────────────
    @app.before_request
    def validate_session():
        """
        If a user_id is in session but the account no longer exists
        (deleted / deactivated between requests), force a logout.
        """
        from flask import request as req
        from .models import User

        uid = session.get('user_id')
        if uid:
            user = User.query.get(uid)
            if not user or not user.is_active:
                session.clear()
                from flask import flash
                flash('Sesi kamu tidak valid atau akun dinonaktifkan. Silakan login ulang.', 'warning')
                # Only redirect if we're not already on an auth route
                if not req.path.startswith('/login') and not req.path.startswith('/logout'):
                    return redirect(url_for('auth.login'))

    # ── Error handlers ─────────────────────────────────────────
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

    return app
