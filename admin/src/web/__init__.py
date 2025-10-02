from flask import Flask
from flask import render_template
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

    @app.route("/")
    def home():
        return render_template("home.html")

    # Register blueprints
    app.register_blueprint(sitios_historicos_bp)
    app.register_blueprint(user_management_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(auth_bp)

    app.register_error_handler(404, error.not_found)
    app.register_error_handler(401, error.unauthorized)
    app.register_error_handler(500, error.server_error)

    #register session handler
    app.jinja_env.globals['is_autenticated'] = is_autenticated

    # register commands

    @app.cli.command("reset-db")
    def reset_db():
        database.reset_db()

    @app.cli.command("seed-db")
    def seed_db():
        seeds.run()

    return app
