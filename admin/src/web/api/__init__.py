from flask import Blueprint

bp = Blueprint("api", __name__, url_prefix="/api")

from . import sitio_historico  # noqa: E402,F401
