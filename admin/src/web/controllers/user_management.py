from flask import Blueprint
from flask import render_template
from flask import request, redirect, url_for
from flask import session, flash, abort

from src.core import auth
from src.core import board
from src.web.handlers.auth import is_autenticated
from src.web.handlers.auth import login_required
from src.web.handlers.auth import check

bp = Blueprint("usuarios", __name__, url_prefix="/manejo_usuarios")


@bp.get("/")
#Este es para que no te deje entrar si no estas logueado
@login_required
@check("user_index")
def index():
    # 1️⃣ Página y paginación
    page = request.args.get("page", 1, type=int)
    per_page = 25  # elementos por página

    # 2️⃣ Filtros desde el query string
    email = request.args.get("email", "").strip()
    activo = request.args.get("activo", "")  # "" | "true" | "false"
    orden = request.args.get("orden", "asc")  # "asc" | "desc"

    # 3️⃣ Obtener todos los usuarios
    todos = auth.list_usuarios()  # lista completa de usuarios

    # 4️⃣ Aplicar filtros
    if email:
        todos = [u for u in todos if email.lower() in u.email.lower()]

    if activo == "true":
        todos = [u for u in todos if u.activo]
    elif activo == "false":
        todos = [u for u in todos if not u.activo]

    # 5️⃣ Ordenar por fecha de creación
    if orden == "desc":
        todos.sort(key=lambda u: u.fechaCreacion, reverse=True)
    else:
        todos.sort(key=lambda u: u.fechaCreacion)

    # 6️⃣ Paginación
    total = len(todos)
    inicio = (page - 1) * per_page
    fin = inicio + per_page
    usuarios = todos[inicio:fin]

    # 7️⃣ Roles (si los necesitás para algo en el template)
    roles = board.list_roles()

    # 8️⃣ Renderizar con los filtros guardados en el template
    return render_template(
        "manejo_usuarios/user_management.html",
        usuarios=usuarios,
        roles=roles,
        page=page,
        total=total,
        per_page=per_page,
        email=email,
        activo=activo,
        orden=orden
    )


@bp.route("/eliminar/<int:usuario_id>", methods=["POST"])
@login_required
@check("user_destroy")
def eliminar(usuario_id):
    
    user = auth.get_user_by_id(usuario_id)  

    auth.baja_logica_usuario(auth.get_user_by_id(usuario_id))

    return redirect(url_for("usuarios.index"))


@bp.route("/desactivar/<int:usuario_id>", methods=["POST"])
@login_required
@check("user_deactivate")
def desactivar(usuario_id):

    user = auth.get_user_by_id(usuario_id)
    rolesUsuario = auth.listar_roles_usuario(user)
    
    if not "Admin" in rolesUsuario: 
        user.activo = False
        auth.db.session.commit()

    return redirect(url_for("usuarios.index"))


@bp.route("/activar/<int:usuario_id>", methods=["POST"])
@login_required
@check("user_activate")
def activar(usuario_id):
    
    user = auth.get_user_by_id(usuario_id)
    user.activo = True
    auth.db.session.commit()

    return redirect(url_for("usuarios.index"))


@login_required
@check("user_new")
@bp.get("/agregar_usuario")
def agregar_usuario_get():
    # Esto se ejecuta solo cuando el navegador hace GET
    roles = board.list_roles()
    return render_template("manejo_usuarios/formAgregar.html", roles=roles)


@login_required
@check("user_new")
@bp.post("/agregar_usuario")
def agregar_usuario_post():
    # Esto se ejecuta solo cuando se hace POST
    if auth.comprobar_email(request.form["email"]):
        flash("El email ya existe. Por favor, elija otro.", "error")
        return redirect(url_for("usuarios.agregar_usuario_get"))

    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    email = request.form["email"]
    password = request.form["password"]

    if not nombre or not apellido or not email or not password:
        flash('Todos los campos son obligatorios','error')
        return redirect(url_for("usuarios.agregar_usuario_get"))

    roles_ids = request.form.getlist("roles")
    auth.create_user(
        nombre=nombre,
        email=email,
        password=password,
        apellido=apellido,
        activo=True,
        esAdmin=False,
        roles=[board.get_rol_by_id(int(rol_id)) for rol_id in roles_ids]
    )

    return redirect(url_for("usuarios.index"))

@bp.get("/modificar/<int:usuario_id>")
@login_required
@check("user_update")
def modificar_get(usuario_id):

    user = auth.get_user_by_id(usuario_id)
    rolesUsuario = auth.listar_roles_usuario(user)
    roles = board.list_roles()
    return render_template("manejo_usuarios/modificar_usuario.html", usuario=user, roles=roles, rolesUsuario=rolesUsuario) 


@bp.post("/modificar/<int:usuario_id>")
@login_required
@check("user_update")
def modificar_post(usuario_id):
    
    user = auth.get_user_by_id(usuario_id)
    return funcion_modificar(user,request.form)


@bp.get("/modificar_mi_perfil")
@login_required
@check("profile_update")
def modificar_mi_perfil_get():

    user = auth.get_user_by_id(session['user_id'])
    rolesUsuario = auth.listar_roles_usuario(user)
    roles = board.list_roles()
    return render_template("manejo_usuarios/modificar_perfil.html", usuario=user, roles=roles, rolesUsuario=rolesUsuario) 


@bp.post("/modificar_mi_perfil")
@login_required
@check("profile_update")
def modificar_mi_perfil_post():
    
    user = auth.get_user_by_id(session['user_id'])
    return funcion_modificar(user,request.form)



def funcion_modificar(user,form):

    nombre = form["nombre"]
    apellido = form["apellido"]
    email = form["email"]

    if not nombre or not apellido or not email:
        flash('Todos los campos son obligatorios','error')
        return redirect(url_for("usuarios.index"))
    
    user.nombre = nombre
    user.apellido = apellido
    user.email = email

    roles_ids = form.getlist("rol")
    user.roles = [board.get_rol_by_id(int(rol_id)) for rol_id in roles_ids]

    session['username'] = user.nombre
    auth.db.session.commit()

    return redirect(url_for("usuarios.index"))


@bp.get("/detalles/<int:usuario_id>")
@login_required
@check("user_show")
def ver_detalles(usuario_id):

    usuario = auth.get_user_by_id(usuario_id)
    roles = auth.listar_roles_usuario(usuario)
    return render_template("manejo_usuarios/detalles_usuario.html", usuario=usuario, roles=roles)

@bp.get("/miperfil")
@login_required
@check("profile_show")
def ver_perfil():

    usuario = auth.get_user_by_id(session['user_id'])
    roles = auth.listar_roles_usuario(usuario)

    return render_template("manejo_usuarios/mi_perfil.html", usuario=usuario, roles=roles)





@bp.route("/cambiar_contraseña/<int:usuario_id>", methods=["GET", "POST"])
@login_required
@check("change_password")
def cambiar_contraseña(usuario_id):
    
    user = auth.get_user_by_id(usuario_id)
    step = request.form.get("step")

    # Verificamos si el usuario es admin
    es_admin = any(rol.nombre == "Admin" for rol in user.roles)

    # Si es admin, no necesita verificar contraseña
    if es_admin and not step:
        # Renderiza directamente la parte del cambio
        return render_template("manejo_usuarios/cambiar_contraseña.html", verified=True, usuario=user)

    # Paso 1: verificar contraseña actual
    if step == "verify":
        contraseña_actual = request.form.get("contraseña_actual")

        if user and auth.check_password(user, contraseña_actual):
            flash("Contraseña actual verificada.", "success")
            return render_template("manejo_usuarios/cambiar_contraseña.html", verified=True, usuario=user)
        else:
            flash("La contraseña actual no es correcta.", "error")

    # Paso 2: guardar nueva contraseña
    elif step == "change":
        nueva = request.form.get("nueva_contraseña")
        repetir = request.form.get("repetir_contraseña")

        if nueva != repetir:
            flash("Las contraseñas no coinciden.", "error")
            return render_template("manejo_usuarios/cambiar_contraseña.html", verified=True, usuario=user)

        auth.update_password(usuario_id, nueva)

        flash("Contraseña cambiada correctamente.", "success")
        return redirect(url_for("home"))

    
    return render_template("manejo_usuarios/cambiar_contraseña.html", verified=False, usuario=user)


