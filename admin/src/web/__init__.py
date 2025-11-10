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
from src.web.api.sites import bp as sites_api_bp
from src.core import seeds
from src.web.controllers.auth import bp as auth_bp
from src.core.bcrypt import bcrypt
from src.web.handlers.auth import is_autenticated, check_permission, is_system_admin
from src.core import auth as core_auth
from src.core.entity.services import feature_flags as ff_service
from src.core.entity.services.feature_flags import get_flag
from src.web.controllers.feature_flags import bp as feature_flags_bp

session = Session()


def create_app(env="development", static_folder="../../static"):
    app = Flask(__name__, static_folder=static_folder)
    app.config.from_object(config[env])
    app.config['JSON_SORT_KEYS'] = False

    database.init_db(app)
    session.init_app(app)
    bcrypt.init_app(app)

    with app.app_context():
        try:
            ff_service.ensure_default_flags()
        except Exception:
            pass

    @app.route("/")
    def home():
        return render_template("home.html")

    # Registro blueprints
    app.register_blueprint(sitios_historicos_bp)
    app.register_blueprint(user_management_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(feature_flags_bp)

    app.register_error_handler(403, error.forbidden)
    app.register_error_handler(404, error.not_found)
    app.register_error_handler(401, error.unauthorized)
    app.register_error_handler(500, error.server_error)
    app.register_blueprint(sites_api_bp)

    app.jinja_env.globals['is_autenticated'] = is_autenticated
    app.jinja_env.globals['check_permission'] = check_permission

    # Helper para usar flags en template
    def get_flag_value(nombre: str) -> bool:
        f = get_flag(nombre)
        return bool(f and f.valor)

    def get_flag_message(nombre: str) -> str | None:
        f = get_flag(nombre)
        return f.mensaje if f else None

    app.jinja_env.globals['is_system_admin'] = is_system_admin
    app.jinja_env.globals['get_flag_value'] = get_flag_value
    app.jinja_env.globals['get_flag_message'] = get_flag_message
    # Exponer helper "system admin" (booleano esAdmin) a Jinja
    app.jinja_env.globals['is_system_admin'] = is_system_admin

    @app.before_request
    def enforce_admin_maintenance():
        # Allow static and CLI
        if request.endpoint in (None, 'static'):
            return None
        # Always allow auth routes
        if request.blueprint == 'auth':
            return None
        # Permitir Feature Flags solo a administradores (esAdmin=True)
        if request.blueprint == 'feature_flags':
            if is_system_admin():
                return None
            # No administrador: si hay mantenimiento, se muestra mensaje y se redirige a login
            flag = get_flag('admin_maintenance_mode')
            if flag and flag.valor:
                msg = flag.mensaje or 'Sistema en mantenimiento.'
                flash(msg, 'error')
                return redirect(url_for('auth.login'))
            # Si no hay mantenimiento, igualmente restringimos a admins por seguridad
            flash('No tiene permisos para acceder a esta página', 'error')
            return redirect(url_for('usuarios.index'))

        flag = get_flag('admin_maintenance_mode')
        if flag and flag.valor:
            # Solo administradores (esAdmin=True) pueden navegar el panel durante mantenimiento
            if not is_system_admin():
                msg = flag.mensaje or 'Sistema en mantenimiento.'
                flash(msg, 'error')
                return redirect(url_for('auth.login'))
            # Admins pueden navegar normalmente
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
