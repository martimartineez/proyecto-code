from src.core import board
from flask import Blueprint, render_template, request, redirect, url_for
from src.core.board.usuario import Usuario
from src.core.board import SitioHistorico
from src.core.database import db
from src.core.board.ciudad import Ciudad
from flask import flash
from datetime import datetime
from sqlalchemy import or_
from src.core.board.tag import Tag


bp = Blueprint("sitios_historicos", __name__, url_prefix="/sitioshistoricos")


def _label_es(campo: str) -> str:
    mapping = {
        "nombre": "Nombre",
        "descBreve": "Descripción breve",
        "descCompleta": "Descripción completa",
        "idCiudad": "Ciudad",
        "idCategoria": "Categoría",
        "latitud": "Latitud",
        "longitud": "Longitud",
        "estadoConservacion": "Estado de conservación",
        "anioInauguracion": "Fecha de inauguración",
        "fechaRegistro": "Fecha de registro",
        "visible": "Visible",
        "baja": "Dado de baja",
    }
    return mapping.get(campo, campo)


def _fmt_value(campo: str, valor, ciudades_by_id: dict[int, str], categorias_by_id: dict[int, str]):
    if valor is None or valor == "" or valor == {}:
        return "—"
    if campo == "idCiudad":
        return ciudades_by_id.get(int(valor)) if valor is not None else "—"
    if campo == "idCategoria":
        return categorias_by_id.get(int(valor)) if valor is not None else "—"
    if isinstance(valor, bool):
        return "Sí" if valor else "No"
    # valores fecha en iso string
    try:
        if isinstance(valor, str) and len(valor) >= 10 and valor[4] == "-" and valor[7] == "-":
            return valor[:16].replace("T", " ")
    except Exception:
        pass
    return str(valor)


def _build_historial_view(historial: dict, ciudades, categorias, usuarios_by_id: dict[int, Usuario] | dict[int, str] | None = None):
    ciudades_by_id = {c.id: c.nombre for c in ciudades}
    categorias_by_id = {c.id: c.nombre for c in categorias}
    usuarios_by_id = usuarios_by_id or {}
    items_view = []
    for e in historial["items"]:
        prev = e.valoresAnteriores or {}
        new = e.valoresNuevos or {}
        campos = sorted(set(list(prev.keys()) + list(new.keys())))
        cambios = []
        for campo in campos:
            antes = prev.get(campo)
            despues = new.get(campo)
            if antes == despues:
                continue
            cambios.append({
                "campo": _label_es(campo),
                "antes": _fmt_value(campo, antes, ciudades_by_id, categorias_by_id),
                "despues": _fmt_value(campo, despues, ciudades_by_id, categorias_by_id),
            })
        usuario_label = None
        try:
            u = usuarios_by_id.get(e.idUsuario)
            if isinstance(u, Usuario):
                usuario_label = f"{u.nombre} {u.apellido} <{u.email}>"
            elif isinstance(u, str):
                usuario_label = u
        except Exception:
            usuario_label = None

        items_view.append({
            "fecha": e.fechaAccion,
            "usuario_id": e.idUsuario,
            "usuario": usuario_label or f"#{e.idUsuario}",
            "accion": e.accion,
            "cambios": cambios,
        })
    return {
        "items": items_view,
        "total": historial["total"],
        "page": historial["page"],
        "per_page": historial["per_page"],
        "pages": historial["pages"],
    }


@bp.get("/")
def index():
    sitios_historicos = board.listar_sitios()
    return render_template("sitios_historicos/index.html", sitios=sitios_historicos)


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
    # Filtros de historial
    usuario_id = request.args.get("usuario_id", type=int)
    accion = request.args.get("accion")
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
    page = request.args.get("page", default=1, type=int)
    historial = board.listar_historial_sitio(
        id_sitio=sitio_id,
        usuario_id=usuario_id,
        accion=accion,
        desde=desde,
        hasta=hasta,
        page=page,
        per_page=25,
    )
    provincias = board.listar_provincias()
    ciudades = board.listar_ciudades()
    categorias = board.listar_categorias()
    # construir mapa de usuarios mencionados en historial
    user_ids = {e.idUsuario for e in historial["items"]}
    usuarios = []
    if user_ids:
        usuarios = db.session.query(Usuario).filter(Usuario.id.in_(user_ids)).all()
    usuarios_by_id = {u.id: u for u in usuarios}
    usuarios_historial = [
        {"id": u.id, "label": f"{u.nombre} {u.apellido} <{u.email}>"}
        for u in usuarios
    ]
    historial_view = _build_historial_view(historial, ciudades, categorias, usuarios_by_id)
    tags = board.listar_tags()
    return render_template(
        "sitios_historicos/formEditar.html",
        sitio=sitio,
        provincias=provincias,
        ciudades=ciudades,
        categorias=categorias,
        historial=historial,
        historial_view=historial_view,
        usuarios_historial=usuarios_historial,
        filtros={
            "usuario_id": usuario_id,
            "accion": accion,
            "desde": desde,
            "hasta": hasta,
            "page": page,
        },
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
    # Filtros de historial
    usuario_id = request.args.get("usuario_id", type=int)
    accion = request.args.get("accion")
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
    page = request.args.get("page", default=1, type=int)
    historial = board.listar_historial_sitio(
        id_sitio=sitio_id,
        usuario_id=usuario_id,
        accion=accion,
        desde=desde,
        hasta=hasta,
        page=page,
        per_page=25,
    )
    ciudades = board.listar_ciudades()
    categorias = board.listar_categorias()
    # construir mapa y lista de usuarios para filtros y labels
    user_ids = {e.idUsuario for e in historial["items"]}
    usuarios = []
    if user_ids:
        usuarios = db.session.query(Usuario).filter(Usuario.id.in_(user_ids)).all()
    usuarios_by_id = {u.id: u for u in usuarios}
    usuarios_historial = [
        {"id": u.id, "label": f"{u.nombre} {u.apellido} <{u.email}>"}
        for u in usuarios
    ]
    historial_view = _build_historial_view(historial, ciudades, categorias, usuarios_by_id)
    return render_template(
        "sitios_historicos/ver_sitio.html",
        sitio=sitio,
        historial=historial,
        historial_view=historial_view,
        usuarios_historial=usuarios_historial,
        filtros={
            "usuario_id": usuario_id,
            "accion": accion,
            "desde": desde,
            "hasta": hasta,
            "page": page,
        },
    )
    return render_template("sitios_historicos/ver_sitio.html", sitio=sitio)

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
