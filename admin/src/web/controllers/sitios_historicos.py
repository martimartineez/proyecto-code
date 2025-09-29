from src.core import board
from flask import Blueprint, render_template, request, redirect, url_for
from src.core.board import SitioHistorico
from src.core.database import db
from src.core.board.ciudad import Ciudad
from flask import flash
from datetime import datetime
from sqlalchemy import or_
from src.core.board.tag import Tag


bp = Blueprint("sitios_historicos", __name__, url_prefix="/sitioshistoricos")


@bp.get("/")
def index():
    sitios_historicos = board.listar_sitios()
    return render_template("sitios_historicos/index.html", sitios=sitios_historicos)


@bp.route("/nuevo", methods=["GET", "POST"])
def agregar_sitio():
    if request.method == "POST":
        # Procesar datos y agregar sitio
        board.crear_sitio(request.form)
        return redirect(url_for("sitios_historicos.index"))
    provincias = board.listar_provincias()
    ciudades = board.listar_ciudades()
    categorias = board.listar_categorias()
    return render_template(
        "sitios_historicos/formAgregar.html",
        provincias=provincias,
        ciudades=ciudades,
        categorias=categorias,
    )


@bp.route("/<int:sitio_id>/editar", methods=["GET", "POST"])
def editar_sitio(sitio_id):
    if request.method == "POST":
        # Procesar edición del sitio
        board.editar_sitio(sitio_id, request.form)
        return redirect(url_for("sitios_historicos.index"))
    sitio = board.obtener_sitio(sitio_id)
    provincias = board.listar_provincias()
    ciudades = board.listar_ciudades()
    categorias = board.listar_categorias()
    return render_template(
        "sitios_historicos/formEditar.html",
        sitio=sitio,
        provincias=provincias,
        ciudades=ciudades,
        categorias=categorias,
    )


@bp.post("/<int:sitio_id>/eliminar")
def eliminar_sitio(sitio_id):
    board.eliminar_sitio(sitio_id)
    return redirect(url_for("sitios_historicos.index"))


@bp.route("/busquedaAvanzada", methods=["GET"])
def busqueda_avanzada():
    provincias = board.listar_provincias()
    ciudades = board.listar_ciudades()
    categorias = board.listar_categorias()

    provincia_id = request.args.get("provincia")
    ciudad_id = request.args.get("ciudad")
    categoria_id = request.args.get("categoria")
    estado_conservacion = request.args.get("estado_conservacion")
    fecha_desde = request.args.get("fecha_desde")
    fecha_hasta = request.args.get("fecha_hasta")
    visibilidad = request.args.get("visibilidad")
    page = request.args.get("page", 1, type=int)
    sort_by = request.args.get("sort_by", "fecha_registro")
    order = request.args.get("order", "asc")

    per_page = 5

    query = db.session.query(SitioHistorico)
    buscar = request.args.get("buscar", "").strip()

    if provincia_id:
        query = (
            db.session.query(SitioHistorico)
            .join(Ciudad)
            .filter(Ciudad.idProvincia == provincia_id)
        )
    if ciudad_id:
        query = query.filter(SitioHistorico.idCiudad == ciudad_id)

    if categoria_id:
        query = query.filter(SitioHistorico.idCategoria == categoria_id)

    if estado_conservacion:
        query = query.filter(
            SitioHistorico.estadoConservacion.ilike(f"%{estado_conservacion}%")
        )
    if fecha_desde:
        query = query.filter(SitioHistorico.fechaRegistro >= fecha_desde)

    if fecha_hasta:
        query = query.filter(SitioHistorico.fechaRegistro <= fecha_hasta)

    if visibilidad == "1":
        query = query.filter(SitioHistorico.visible == True)
    elif visibilidad == "0":
        query = query.filter(SitioHistorico.visible == False)

    if buscar:
        query = query.filter(
            (SitioHistorico.nombre.ilike(f"%{buscar}%")) |
            (SitioHistorico.descBreve.ilike(f"%{buscar}%"))
            )

    filtros_aplicados = any(
        [
            provincia_id,
            ciudad_id,
            categoria_id,
            estado_conservacion,
            fecha_desde,
            fecha_hasta,
            visibilidad,
        ]
    )

    valid_sort_columns = {
        "fecha_registro": SitioHistorico.fechaRegistro,
        "nombre": SitioHistorico.nombre,
        "ciudad": Ciudad.nombre,
    }

    if sort_by in valid_sort_columns:
        column = valid_sort_columns[sort_by]
    if order == "desc":
        query = query.order_by(column.desc())
    else:
        query = query.order_by(column.asc())

    from sqlalchemy import or_

    tags_input = request.args.get("tags", "").strip()

    if tags_input:
        tag_nombres = [t.strip() for t in tags_input.split(",") if t.strip()]
        if tag_nombres:
            query = query.join(SitioHistorico.tags).filter(
                or_(*[Tag.nombre.ilike(f"%{t}%") for t in tag_nombres])
            )
    total_results = 0
    total_pages = 0
    query_result = None
    if filtros_aplicados:
        total_results = query.count()
        query_result = query.offset((page - 1) * per_page).limit(per_page).all()
        total_pages = (total_results + per_page - 1) // per_page
    print(query)

    return render_template(
        "sitios_historicos/busquedaAvanzada.html",
        provincias=provincias,
        ciudades=ciudades,
        categorias=categorias,
        sitios=query_result,
        page=page,
        total_pages=total_pages,
        total_results=total_results,
        request_args=request.args.to_dict(),
    )


# a que se refiere con validar fechas.#Si la fecha desde es mayor a la fecha hasta, no deberia devolver ningun resultado.
