from src.core import board
from flask import Blueprint, render_template, request, redirect, url_for

bp = Blueprint("sitios_historicos", __name__, url_prefix="/sitioshistoricos")


@bp.get("/")
def index():
    page = request.args.get("page", 1, type=int)
    per_page = 25
    sitios_historicos = board.listar_sitios(page=page, per_page=per_page)
    total = board.contar_sitios()
    total_pages = (total + per_page - 1) // per_page  # redondeo hacia arriba

    return render_template(
        "sitios_historicos/index.html",
        sitios=sitios_historicos,
        page=page,
        total_pages=total_pages
    )

@bp.route("/nuevo", methods=["GET", "POST"])
def agregar_sitio():
    next_url = request.args.get("next", url_for("sitios_historicos.index"))

    if request.method == "POST":
        # Procesar datos y agregar sitio
        board.crear_sitio(request.form)
        return redirect(url_for("sitios_historicos.index"))
    provincias = board.listar_provincias()
    ciudades = board.listar_ciudades()
    categorias = board.listar_categorias()
    tags = board.listar_tags()
    return render_template(
        "sitios_historicos/formAgregar.html",
        provincias=provincias,
        ciudades=ciudades,
        categorias=categorias,
        tags=tags,
        next_url=next_url,
    )


@bp.route("/<int:sitio_id>/editar", methods=["GET", "POST"])
def editar_sitio(sitio_id):
    next_url = request.args.get("next", url_for("sitios_historicos.index"))

    if request.method == "POST":
        # Procesar edición del sitio
        board.editar_sitio(sitio_id, request.form)
        return redirect(url_for("sitios_historicos.index"))
    sitio = board.obtener_sitio(sitio_id)
    provincias = board.listar_provincias()
    ciudades = board.listar_ciudades()
    categorias = board.listar_categorias()
    tags = board.listar_tags()
    return render_template(
        "sitios_historicos/formEditar.html",
        sitio=sitio,
        provincias=provincias,
        ciudades=ciudades,
        categorias=categorias,
        tags=tags,
        next_url=next_url,
    )


@bp.post("/<int:sitio_id>/eliminar")
def eliminar_sitio(sitio_id):
    board.eliminar_sitio(sitio_id)
    return redirect(url_for("sitios_historicos.index"))

@bp.route("/sitio/<int:sitio_id>")
def ver_sitio(sitio_id):
    sitio = board.obtener_sitio(sitio_id)
    return render_template("sitios_historicos/ver_sitio.html", sitio=sitio)
