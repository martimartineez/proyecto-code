from src.core import board
from flask import Blueprint, render_template, request, redirect, url_for, flash

bp = Blueprint("tags", __name__, url_prefix="/tags")


@bp.get("/")
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



@bp.route("/nuevo", methods=["GET", "POST"])
def agregar_tag():
    if request.method == "POST":
        tag = board.crear_tag(request.form)
        if tag:
            # flash(f"Tag '{tag.nombre}' creado exitosamente.")
            return redirect(url_for("tags.index"))
        # flash("Error al crear el tag.")
        return redirect(url_for("tags.agregar_tag"))

    return render_template("tags/form_tags.html", action="agregar")


@bp.route("/<int:tag_id>/editar", methods=["GET", "POST"])
def editar_tag(tag_id):
    tag = board.obtener_tag(tag_id)
    if not tag:
        # flash("Tag no encontrado.")
        return redirect(url_for("tags.index"))

    if request.method == "POST":
        if board.editar_tag(tag_id, request.form):
            # flash(f"Tag '{tag.nombre}' editado exitosamente.")
            return redirect(url_for("tags.index"))
        # flash("Error al editar el tag.")
        return redirect(url_for("tags.editar_tag", tag_id=tag_id))

    return render_template("tags/form_tags.html", tag=tag, action="editar")


@bp.post("/<int:tag_id>/eliminar")
def eliminar_tag(tag_id):
    resultado = board.eliminar_tag(tag_id)
    
    if resultado is True:
        flash("Tag eliminado exitosamente.", "success")
    elif resultado == "vinculado":
        # Manejamos el error específico de la restricción M:N
        flash("ERROR: El Tag no puede ser eliminado porque está asociado a uno o más Sitios Históricos. Desvincúlelo primero.", "error")
    else: 
        flash("ERROR: El Tag no pudo ser eliminado (no encontrado o error desconocido).", "error")
        
    return redirect(url_for("tags.index"))