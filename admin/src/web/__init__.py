from flask import Flask
from flask import render_template
from src.core import database
from src.web.handlers import error
from src.web.config import config
from src.core import database
from src.web.controllers.sitios_historicos import bp as sitios_historicos_bp
from src.core import seeds


def create_app(env="development", static_folder="../../static"):
    app = Flask(__name__, static_folder=static_folder)
    app.config.from_object(config[env])

    # initialize database
    database.init_db(app)

    @app.route("/")
    def home():
        return render_template("home.html")

    # register blueprints
    app.register_blueprint(sitios_historicos_bp)

    app.register_error_handler(404, error.not_found)
    app.register_error_handler(401, error.unauthorized)
    app.register_error_handler(500, error.server_error)

    # register commands

    @app.cli.command("reset-db")
    def reset_db():
        database.reset_db()

    @app.cli.command("seed-db")
    def seed_db():
        seeds.run()

    return app