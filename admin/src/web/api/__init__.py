from flask import Blueprint

bp = Blueprint("api", __name__, url_prefix="/api")

from . import sites  # noqa: E402,F401
from . import feature_flags  # noqa: E402,F401
