from flask import Flask
from flask import render_template, request, redirect, url_for, flash
from flask_session import Session
from src.core import database
from src.web.handlers import error
from src.web.config import config
from src.core import database
from src.web.controllers.sitios_historicos import bp as sitios_historicos_bp
from src.web.controllers.tags import bp as tags_bp
from src.web.controllers.user_management import bp as user_management_bp
from src.web.controllers.tags import bp as tags_bp
from src.core import seeds
from src.web.controllers.auth import bp as auth_bp
from src.core.bcrypt import bcrypt
from src.web.handlers.auth import is_autenticated
from src.core import auth as core_auth
from src.core.board import feature_flags as ff_service
from src.core.board.feature_flags import get_flag
from src.web.controllers.feature_flags import bp as feature_flags_bp

session = Session()


def create_app(env="development", static_folder="../../static"):
    app = Flask(__name__, static_folder=static_folder)
    app.config.from_object(config[env])

    # initialize database
    database.init_db(app)
    # initialize session
    session.init_app(app)
    # initialize bcrypt
    bcrypt.init_app(app)

    # Ensure default feature flags exist
    with app.app_context():
        try:
            ff_service.ensure_default_flags()
        except Exception:
            # DB may not be ready yet for CLI commands like reset-db
            pass

    @app.route("/")
    def home():
        return render_template("home.html")

    # Register blueprints
    app.register_blueprint(sitios_historicos_bp)
    app.register_blueprint(user_management_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(feature_flags_bp)

    app.register_error_handler(403, error.forbidden)
    app.register_error_handler(404, error.not_found)
    app.register_error_handler(401, error.unauthorized)
    app.register_error_handler(500, error.server_error)

    #register session handler and helpers
    app.jinja_env.globals['is_autenticated'] = is_autenticated

    # Local helper for admin check (user.esAdmin)
    def is_admin() -> bool:
        from flask import session as _session
        uid = _session.get('user_id')
        if not uid:
            return False
        u = core_auth.get_user_by_id(uid)
        return bool(u and getattr(u, 'esAdmin', False))

    app.jinja_env.globals['is_admin'] = is_admin

    # Simple helpers to use flags in templates
    def get_flag_value(nombre: str) -> bool:
        f = get_flag(nombre)
        return bool(f and f.valor)

    def get_flag_message(nombre: str) -> str | None:
        f = get_flag(nombre)
        return f.mensaje if f else None

    app.jinja_env.globals['get_flag_value'] = get_flag_value
    app.jinja_env.globals['get_flag_message'] = get_flag_message

    @app.before_request
    def enforce_admin_maintenance():
        # Allow static and CLI
        if request.endpoint in (None, 'static'):
            return None
        # Always allow auth routes
        if request.blueprint == 'auth':
            return None
        # Allow Feature Flags page for any usuario logueado (route has @login_required)
        if request.blueprint == 'feature_flags':
            return None

        flag = get_flag('admin_maintenance_mode')
        if flag and flag.valor:
            # If logged-in users navigate anywhere, show banner via flash and redirect to login for non-admins
            if not is_admin():
                msg = flag.mensaje or 'Sistema en mantenimiento.'
                flash(msg, 'error')
                return redirect(url_for('auth.login'))
            # Admins can navigate normally
            return None
        return None

    # register commands

    @app.cli.command("reset-db")
    def reset_db():
        database.reset_db()

    @app.cli.command("seed-db")
    def seed_db():
        seeds.run()

    return app
