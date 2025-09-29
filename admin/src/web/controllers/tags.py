from src.core import board
from flask import Blueprint, render_template, request, redirect, url_for, flash

bp = Blueprint("tags", __name__, url_prefix="/tags")


@bp.get("/")
def index():
    tags = board.listar_tags()
    return render_template("tags/index_tags.html", tags=tags)


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
    """Lógica para eliminar un tag."""
    if board.eliminar_tag(tag_id):
        # flash("Tag eliminado exitosamente.")
        pass # Por si no usas flash
    else:
        # flash("Error al eliminar el tag o tag no encontrado.")
        pass # Por si no usas flash
    
    return redirect(url_for("tags.index"))