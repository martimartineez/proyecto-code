from flask import Blueprint
from flask import render_template
from flask import request, redirect, url_for

from src.core import auth
from src.core import board

bp = Blueprint("usuarios", __name__, url_prefix="/manejo_usuarios")


@bp.get("/")
def index():
    usuarios = auth.list_usuarios()
    roles = board.list_roles()

    return render_template("manejo_usuarios/user_management.html", usuarios=usuarios, roles=roles)

@bp.route("/manejo_usuarios", methods=["POST"])
def agregar():
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    email = request.form["email"]
    password = request.form["password"]
    #rol = request.form.get("rol") preguntarle al profe de los roles

    auth.create_user(
        nombre=nombre,
        email=email,
        password=password,
        apellido=apellido,
        activo=True,
        esAdmin=True,
        idRol=1
    )

    # Redirigir al index dentro del blueprint
    return redirect(url_for("usuarios.index"))
