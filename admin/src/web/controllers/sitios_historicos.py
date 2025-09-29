from src.core import board
from flask import Blueprint, render_template, request, redirect, url_for
from src.core.database import db
from src.core.board.usuario import Usuario

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
    return render_template(
        "sitios_historicos/formAgregar.html",
        provincias=provincias,
        ciudades=ciudades,
        categorias=categorias,
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
