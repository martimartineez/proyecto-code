from src.core import board
from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.web.handlers.auth import login_required, check
from core.board.validaciones import validar_tag

bp = Blueprint("tags", __name__, url_prefix="/tags")


@bp.get("/")
@login_required
@check("tag_index")
def index():
    page = request.args.get("page", 1, type=int)
    per_page = 25
    q = request.args.get("q", None)
    sort = request.args.get("sort", "nombre")  # puede ser "nombre,fecha"
    order = request.args.get("order", "asc")

    tags = board.listar_tags(page=page, per_page=per_page, q=q, sort=sort, order=order)
    total = board.contar_tags(q=q)
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        "tags/index_tags.html",
        tags=tags,
        page=page,
        total_pages=total_pages,
        q=q,
        sort=sort,
        order=order
    )

@bp.get("/nuevo")
@login_required
@check("tag_create")
def agregar_tag_get():
    return render_template("tags/form_tags.html", action="agregar")

@bp.post("/nuevo")
@login_required
@check("tag_create")
def agregar_tag_post():
    # Validar datos con la capa separada
    errores = validar_tag(request.form)
    
    if errores:
        # Mostrar errores en flash messages y re-renderizar
        for campo, msg in errores.items():
            flash(f"{msg}", "error")
        # Devolver el formulario con los datos ingresados
        return render_template("tags/form_tags.html", action="agregar", form_data=request.form), 400
    
    resultado = board.crear_tag(request.form)
    
    if resultado and resultado != "DUPLICATE_ERROR":
        # Caso 1: Éxito
        flash("Tag agregado exitosamente.", "success")
        return redirect(url_for("tags.index"))
    
    elif resultado == "DUPLICATE_ERROR":
        # Caso 2: El Tag ya existe
        flash(f"Error: Ya existe un Tag con el nombre '{request.form.get('nombre')}' o uno muy similar.", "error")
        
    else:
        # Caso 3: Otro error (ej: error de servidor o nombre vacío)
        flash("Ocurrió un error inesperado al intentar agregar el Tag.", "error")
        
    # Si el POST falló (Casos 2 y 3), se vuelve a renderizar el formulario con el mensaje flash
    return render_template("tags/form_tags.html", action="agregar", form_data=request.form)



# @bp.route("/nuevo", methods=["GET", "POST"])
# @login_required
# @check("tag_create")
# def agregar_tag():
#     if request.method == "POST":
#         # Validar datos con la capa separada
#         errores = validar_tag(request.form)
        
#         if errores:
#             # Mostrar errores en flash messages y re-renderizar
#             for campo, msg in errores.items():
#                 # Nota: Uso "flash" con categoría "error"
#                 flash(f"{msg}", "error")
#             # Devolver el formulario con los datos ingresados para que no los pierda (opcional)
#             return render_template("tags/form_tags.html", action="agregar", form_data=request.form), 400
        
#         resultado = board.crear_tag(request.form)
        
#         if resultado and resultado != "DUPLICATE_ERROR":
#             # Caso 1: Éxito
#             flash("Tag agregado exitosamente.", "success")
#             return redirect(url_for("tags.index"))
        
#         elif resultado == "DUPLICATE_ERROR":
#             # Caso 2: El Tag ya existe
#             flash(f"Error: Ya existe un Tag con el nombre '{request.form.get('nombre')}' o uno muy similar.", "error")
#             # Dejamos que la ejecución siga para que se vuelva a renderizar el formulario
            
#         else:
#             # Caso 3: Otro error (ej: error de servidor o nombre vacío)
#             flash("Ocurrió un error inesperado al intentar agregar el Tag.", "error")
            
#     # Si es GET o si el POST falló (Casos 2 y 3), se renderiza el formulario
#     return render_template("tags/form_tags.html", action="agregar")



@bp.get("/<int:tag_id>/editar")
@login_required
@check("tag_update")
def editar_tag_get(tag_id):
    tag = board.obtener_tag(tag_id)
    if not tag:
        flash("Tag no encontrado.", "error")
        return redirect(url_for("tags.index"))
    # Renderiza el formulario con los datos del tag
    return render_template("tags/form_tags.html", tag=tag, action="editar")

@bp.post("/<int:tag_id>/editar")
@login_required
@check("tag_update")
def editar_tag_post(tag_id):
    tag = board.obtener_tag(tag_id)
    if not tag:
        flash("Tag no encontrado.", "error")
        return redirect(url_for("tags.index"))

    # Validar datos con la capa separada
    errores = validar_tag(request.form)
    
    if errores:
        # Mostrar errores y re-renderizar
        for campo, msg in errores.items():
            flash(f"{msg}", "error")
        # Devolver el formulario con el tag existente y los datos POST
        return render_template("tags/form_tags.html", tag=tag, action="editar", form_data=request.form), 400

    resultado = board.editar_tag(tag_id, request.form)
    
    if resultado is True:
        # Caso 1: Éxito (incluye si el nombre no se modificó)
        flash("Tag editado exitosamente.", "success")
        return redirect(url_for("tags.index"))
    
    elif resultado == "DUPLICATE_ERROR":
        # Caso 2: El nuevo nombre/slug ya existe en OTRO tag
        flash(f"Error: Ya existe un Tag con el nombre '{request.form.get('nombre')}' o no esta disponible para usar.", "error")
        
    else:
        # Caso 3: Otro error (servidor, nombre vacío)
        flash("Ocurrió un error inesperado al intentar editar el Tag.", "error")
    
    # Si el POST falló (Casos 2 y 3), se vuelve a renderizar el formulario con el mensaje flash
    return render_template("tags/form_tags.html", tag=tag, action="editar", form_data=request.form)

# @bp.route("/<int:tag_id>/editar", methods=["GET", "POST"])
# @login_required
# @check("tag_update")
# def editar_tag(tag_id):
#     tag = board.obtener_tag(tag_id)
#     if not tag:
#         flash("Tag no encontrado.", "error")
#         return redirect(url_for("tags.index"))

#     if request.method == "POST":
#         # Validar datos con la capa separada
#         errores = validar_tag(request.form)
        
#         if errores:
#             # Mostrar errores y re-renderizar
#             for campo, msg in errores.items():
#                 flash(f"{msg}", "error")
#             # Devolver el formulario con el tag existente y los datos POST
#             return render_template("tags/form_tags.html", tag=tag, action="editar", form_data=request.form), 400


#         resultado = board.editar_tag(tag_id, request.form)
        
#         if resultado is True:
#             # Caso 1: Éxito (incluye si el nombre no se modificó)
#             flash("Tag editado exitosamente.", "success")
#             return redirect(url_for("tags.index"))
        
#         elif resultado == "DUPLICATE_ERROR":
#             # Caso 2: El nuevo nombre/slug ya existe en OTRO tag
#             flash(f"Error: Ya existe un Tag con el nombre '{request.form.get('nombre')}' o no esta disponible para usar.", "error")
#             # Dejamos que el flujo continúe para que se muestre el formulario de edición con el error
            
#         else:
#             # Caso 3: Otro error (servidor, nombre vacío)
#             flash("Ocurrió un error inesperado al intentar editar el Tag.", "error")

#     # Renderiza el formulario (GET o después de un error POST)
#     return render_template("tags/form_tags.html", tag=tag, action="editar")


@bp.post("/<int:tag_id>/eliminar")
@login_required
@check("tag_destroy")
def eliminar_tag(tag_id):
    resultado = board.eliminar_tag(tag_id) # Si retorna una lista, es error.
    
    if resultado is True:
        flash("Tag eliminado exitosamente.", "success")
        
    elif isinstance(resultado, list):
        # ... este código se ejecuta SOLO si hay sitios ACTIVOS vinculados.
        sitios_nombres = ", ".join(resultado)
        flash(f"ERROR: El Tag no puede ser eliminado. Está asociado a los siguientes Sitios Históricos: {sitios_nombres}. Desvincúlelo(s) primero.", "error")
        
    else: 
        flash("Ocurrió un error inesperado al intentar eliminar el Tag.", "error")
        
    return redirect(url_for("tags.index"))