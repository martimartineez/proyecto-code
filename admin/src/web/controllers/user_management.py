from flask import Blueprint
from flask import render_template
from flask import request, redirect, url_for
from flask import session, flash, abort

from src.core import auth
from src.core import board
from src.web.handlers.auth import is_autenticated
from src.web.handlers.auth import login_required
from src.web.handlers.auth import check_permission

bp = Blueprint("usuarios", __name__, url_prefix="/manejo_usuarios")


@bp.get("/")
#Este es para que no te deje entrar si no estas logueado
@login_required
def index():

    if not check_permission("user_index"):
        return abort(403)
    
    usuarios = auth.list_usuarios()
    roles = board.list_roles()

    return render_template("manejo_usuarios/user_management.html", usuarios=usuarios, roles=roles)


@bp.route("/eliminar/<int:usuario_id>", methods=["POST"])
@login_required
def eliminar(usuario_id):
    user = auth.get_user_by_id(usuario_id)
    # Eliminacion fisica
    # if user:
    #     auth.delete_user(user)

    auth.baja_logica_usuario(auth.get_user_by_id(usuario_id))

    return redirect(url_for("usuarios.index"))

@bp.route("/desactivar/<int:usuario_id>", methods=["POST"])
@login_required
def desactivar(usuario_id):
    user = auth.get_user_by_id(usuario_id)
    user.activo = False
    auth.db.session.commit()

    return redirect(url_for("usuarios.index"))


@bp.route("/AgregarUsuario", methods=["GET","POST"])
@login_required
def agregar_usuario():
    if request.method == "POST":
        if (auth.comprobar_email(request.form["email"])):
            flash("El email ya existe. Por favor, elija otro.", "error")
            return redirect(url_for("usuarios.agregar_usuario"))
        else:
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
                idRol=rol,
            )
            # Redirigir al index dentro del blueprint
            return redirect(url_for("usuarios.index"))
    else:
        roles = board.list_roles()
        return render_template("manejo_usuarios/formAgregar.html", roles=roles)

@bp.route("/modificar/<int:usuario_id>", methods=["GET", "POST"])
@login_required
def modificar(usuario_id):
    user = auth.get_user_by_id(usuario_id)
    roles = board.list_roles()

    if request.method == "POST":
        user.nombre = request.form["nombre"]
        user.apellido = request.form["apellido"]
        user.email = request.form["email"]
        user.idRol = int(request.form["rol"])
        session['username'] = user.nombre

        # Guardar los cambios en la base de datos
        auth.db.session.commit()

        return redirect(url_for("usuarios.index"))

    return render_template("manejo_usuarios/modificar_usuario.html", usuario=user, roles=roles) 

@bp.route("/detalles/<int:usuario_id>", methods=["GET", "POST"])
@login_required
def ver_detalles(usuario_id):

    if request.method == "POST":
        usuario = auth.get_user_by_id(usuario_id)
        roles = board.list_roles()
        return render_template("manejo_usuarios/detalles_usuario.html", usuario=usuario, roles=roles)
    
    return redirect(url_for("usuarios.index"))


@bp.route("/cambiar_contraseña/<int:usuario_id>", methods=["GET", "POST"])
@login_required
def cambiar_contraseña(usuario_id):
    user = auth.get_user_by_id(usuario_id)
    step = request.form.get("step")
    # Paso 1: verificar contraseña actual
    if step == "verify":
        contraseña_actual = request.form.get("contraseña_actual")

        if user and auth.check_password(user, contraseña_actual):
            flash("Contraseña actual verificada.", "success")
            return render_template("manejo_usuarios/cambiar_contraseña.html", verified=True)
        else:
            flash("La contraseña actual no es correcta.", "error")


    #return render_template("manejo_usuarios/cambiar_contraseña.html", usuario=user)

    # Paso 2: guardar nueva contraseña
    elif step == "change":
        nueva = request.form.get("nueva_contraseña")
        repetir = request.form.get("repetir_contraseña")

        if nueva != repetir:
            flash("Las contraseñas no coinciden.", "danger")
            return render_template("manejo_usuarios/cambiar_contraseña.html", verified=True)

        auth.update_password(usuario_id, nueva)

        flash("Contraseña cambiada correctamente.", "success")
        return redirect(url_for("usuarios.index"))

    return render_template("manejo_usuarios/cambiar_contraseña.html", verified=False)

@bp.route("/busqueda_avanzada", methods=["GET", "POST"])
@login_required
def busqueda_avanzada():
    # Capturamos los filtros
    email = request.args.get("email", "").strip()
    activo = request.args.get("activo", "")  # puede ser "", "true", "false"
    orden = request.args.get("orden", "asc")  # "asc" o "desc"

    # Arrancamos con la lista de usuarios
    usuarios = auth.list_usuarios()  # Supongo que devuelve una lista/query

    # Filtrar por email
    if email:
        usuarios = [u for u in usuarios if email.lower() in u.email.lower()]

    # Filtrar por activo
    if activo == "true":
        usuarios = [u for u in usuarios if u.activo]
    elif activo == "false":
        usuarios = [u for u in usuarios if not u.activo]

    # Ordenar por fecha (ejemplo: campo u.fecha_creacion)
    usuarios = sorted(
        usuarios,
        key=lambda u: u.fechaCreacion,
        reverse=(orden == "desc")
    )

    return render_template("manejo_usuarios/busqueda_avanzada.html",usuarios=usuarios,email=email,activo=activo,orden=orden)


