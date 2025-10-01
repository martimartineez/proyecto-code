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
    rol = request.form.get("roles")
    if rol == "Admin":
        admin = True
    else:
        admin = False
    #rol = request.form.get("rol") preguntarle al profe de los roles

    auth.create_user(
        nombre=nombre,
        email=email,
        password=password,
        apellido=apellido,
        activo=True,
        esAdmin=admin,
        idRol=rol
    )

    # Redirigir al index dentro del blueprint
    return redirect(url_for("usuarios.index"))

@bp.route("/eliminar/<int:usuario_id>", methods=["POST"])
def eliminar(usuario_id):
    user = auth.get_user_by_id(usuario_id)
    # Eliminacion fisica
    # if user:
    #     auth.delete_user(user)

    auth.baja_logica_usuario(auth.get_user_by_id(usuario_id))

    return redirect(url_for("usuarios.index"))

@bp.route("/modificar/<int:usuario_id>", methods=["GET", "POST"])
def modificar(usuario_id):
    user = auth.get_user_by_id(usuario_id)
    roles = board.list_roles()

    if request.method == "POST":
        user.nombre = request.form["nombre"]
        user.apellido = request.form["apellido"]
        user.email = request.form["email"]
        user.password = request.form["password"]
        user.idRol = int(request.form["rol"])

        # Guardar los cambios en la base de datos
        auth.db.session.commit()

        return redirect(url_for("usuarios.index"))

    return render_template("manejo_usuarios/modificar_usuario.html", usuario=user, roles=roles) 
