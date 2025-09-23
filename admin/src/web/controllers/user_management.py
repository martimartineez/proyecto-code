from flask import Blueprint
from flask import render_template
from src.core import board

bp = Blueprint("issues", __name__, url_prefix="/manejo_usuarios")

@bp.get("/")

def index():
    issues = board.list_issues()
    return render_template("user_management.html", issues=issues)