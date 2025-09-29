from datetime import datetime, timedelta
from src.core.database import db
from src.core.board.sitio_historico import SitioHistorico
from src.core.board.historial_sitio import HistorialSitio
from src.core.board.provincia import Provincia
from src.core.board.ciudad import Ciudad
from src.core.board.categoria_sitio import CategoriaSitio  # noqa: F401
from src.core.board.tag import Tag  # noqa: F401


def _parse_float(value):
    try:
        return float(value) if value not in (None, "") else None
    except Exception:
        return None


def _parse_int(value):
    try:
        return int(value) if value not in (None, "") else None
    except Exception:
        return None


def _parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date() if value else None
    except Exception:
        return None


def listar_sitios():
    return (
        db.session.query(SitioHistorico)
        .order_by(SitioHistorico.id)
        .filter_by(baja=False)
        .all()
    )


def listar_provincias():
    return db.session.query(Provincia).order_by(Provincia.nombre).all()


def listar_ciudades(id_provincia: int | None = None):
    q = db.session.query(Ciudad)
    if id_provincia is not None:
        q = q.filter(Ciudad.idProvincia == id_provincia)
    return q.order_by(Ciudad.nombre).all()


def listar_categorias():
    return db.session.query(CategoriaSitio).order_by(CategoriaSitio.nombre).all()


def registrar_evento_historial(
    id_sitio: int,
    id_usuario: int,
    accion: str,
    valores_anteriores: dict | None = None,
    valores_nuevos: dict | None = None,
):
    evento = HistorialSitio(
        idSitio=id_sitio,
        idUsuario=id_usuario,
        accion=accion,
        valoresAnteriores=valores_anteriores,
        valoresNuevos=valores_nuevos,
    )
    db.session.add(evento)
    db.session.commit()
    return evento


def crear_sitio(form, id_usuario: int | None = None):
    nuevo = SitioHistorico(
        nombre=form.get("nombre"),
        descBreve=form.get("descripcion"),
        descCompleta=form.get("descripcion_completa"),
        idCiudad=_parse_int(form.get("ciudad")),
        idCategoria=_parse_int(form.get("categoria")),
        latitud=_parse_float(form.get("latitud")),
        longitud=_parse_float(form.get("longitud")),
        estadoConservacion=form.get("estado_conservacion"),
        anioInauguracion=_parse_date(form.get("fecha_inauguracion")),
        fechaRegistro=_parse_date(form.get("fecha_registro")) or datetime.now(),
        visible=True,
        baja=False,
    )
    db.session.add(nuevo)
    db.session.commit()
    # Registro de historial
    if id_usuario is None:
        id_usuario = 1  # TODO: reemplazar por usuario autenticado
    try:
        registrar_evento_historial(
            id_sitio=nuevo.id,
            id_usuario=id_usuario,
            accion="CREATED",
            valores_anteriores=None,
            valores_nuevos={
                "nombre": nuevo.nombre,
                "idCiudad": nuevo.idCiudad,
                "idCategoria": nuevo.idCategoria,
                "latitud": nuevo.latitud,
                "longitud": nuevo.longitud,
                "visible": nuevo.visible,
                "baja": nuevo.baja,
            },
        )
    except Exception:
        db.session.rollback()
    return nuevo


def obtener_sitio(sitio_id: int):
    return db.session.get(SitioHistorico, sitio_id)


def editar_sitio(sitio_id: int, form, id_usuario: int | None = None):
    sitio = obtener_sitio(sitio_id)
    if not sitio:
        return False

    # snapshot de valores anteriores relevantes
    prev = {
        "nombre": sitio.nombre,
        "descBreve": sitio.descBreve,
        "descCompleta": sitio.descCompleta,
        "idCiudad": sitio.idCiudad,
        "idCategoria": sitio.idCategoria,
        "latitud": sitio.latitud,
        "longitud": sitio.longitud,
        "estadoConservacion": sitio.estadoConservacion,
        "anioInauguracion": sitio.anioInauguracion.isoformat() if getattr(sitio, "anioInauguracion", None) else None,
        "fechaRegistro": sitio.fechaRegistro.isoformat() if getattr(sitio, "fechaRegistro", None) else None,
        "visible": sitio.visible,
        "baja": sitio.baja,
    }

    sitio.nombre = form.get("nombre") or sitio.nombre
    sitio.descBreve = form.get("descripcion") or sitio.descBreve
    sitio.descCompleta = form.get("descripcion_completa") or sitio.descCompleta
    sitio.idCiudad = _parse_int(form.get("ciudad")) or sitio.idCiudad
    sitio.idCategoria = _parse_int(form.get("categoria")) or sitio.idCategoria
    sitio.latitud = _parse_float(form.get("latitud")) if form.get("latitud") is not None else sitio.latitud
    sitio.longitud = _parse_float(form.get("longitud")) if form.get("longitud") is not None else sitio.longitud
    sitio.estadoConservacion = form.get("estado_conservacion") or sitio.estadoConservacion
    anio = _parse_date(form.get("fecha_inauguracion"))
    if anio:
        sitio.anioInauguracion = anio
    fecha_reg = _parse_date(form.get("fecha_registro"))
    if fecha_reg:
        sitio.fechaRegistro = fecha_reg
    if form.get("visible") is not None:
        sitio.visible = True if form.get("visible") in ("True", True) else False

    db.session.commit()
    # Registro de historial
    if id_usuario is None:
        id_usuario = 1  # TODO: reemplazar por usuario autenticado
    nuevos = {
        "nombre": sitio.nombre,
        "descBreve": sitio.descBreve,
        "descCompleta": sitio.descCompleta,
        "idCiudad": sitio.idCiudad,
        "idCategoria": sitio.idCategoria,
        "latitud": sitio.latitud,
        "longitud": sitio.longitud,
        "estadoConservacion": sitio.estadoConservacion,
        "anioInauguracion": sitio.anioInauguracion.isoformat() if getattr(sitio, "anioInauguracion", None) else None,
        "fechaRegistro": sitio.fechaRegistro.isoformat() if getattr(sitio, "fechaRegistro", None) else None,
        "visible": sitio.visible,
        "baja": sitio.baja,
    }
    try:
        registrar_evento_historial(
            id_sitio=sitio.id,
            id_usuario=id_usuario,
            accion="UPDATED",
            valores_anteriores=prev,
            valores_nuevos=nuevos,
        )
    except Exception:
        db.session.rollback()


def eliminar_sitio(sitio_id: int, id_usuario: int | None = None):
    sitio = obtener_sitio(sitio_id)
    if not sitio:
        return False
    prev_baja = sitio.baja
    sitio.baja = True
    db.session.commit()
    # Registro de historial
    if id_usuario is None:
        id_usuario = 1  # TODO: reemplazar por usuario autenticado
    try:
        registrar_evento_historial(
            id_sitio=sitio.id,
            id_usuario=id_usuario,
            accion="DELETED" if not prev_baja and sitio.baja else "STATE_CHANGED",
            valores_anteriores={"baja": prev_baja},
            valores_nuevos={"baja": sitio.baja},
        )
    except Exception:
        db.session.rollback()
        raise


def listar_historial_sitio(
    id_sitio: int,
    usuario_id: int | None = None,
    accion: str | None = None,
    desde: str | None = None,
    hasta: str | None = None,
    page: int = 1,
    per_page: int = 25,
):
    q = db.session.query(HistorialSitio).filter(HistorialSitio.idSitio == id_sitio)
    if usuario_id:
        q = q.filter(HistorialSitio.idUsuario == usuario_id)
    if accion:
        q = q.filter(HistorialSitio.accion == accion)
    # Parse fechas YYYY-MM-DD
    if desde:
        try:
            d = datetime.strptime(desde, "%Y-%m-%d")
            q = q.filter(HistorialSitio.fechaAccion >= d)
        except Exception:
            pass
    if hasta:
        try:
            h = datetime.strptime(hasta, "%Y-%m-%d") + timedelta(days=1)
            q = q.filter(HistorialSitio.fechaAccion < h)
        except Exception:
            pass

    q = q.order_by(HistorialSitio.fechaAccion.desc())
    total = q.count()
    if page < 1:
        page = 1
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if per_page else 1,
    }
