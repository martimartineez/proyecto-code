from datetime import datetime
from src.core.database import db
from src.core.board.sitio_historico import SitioHistorico
from src.core.board.provincia import Provincia
from src.core.board.ciudad import Ciudad
from src.core.board.categoria_sitio import CategoriaSitio  # noqa: F401
from src.core.board.tag import Tag  # noqa: F401
from src.core.auth.usuario import Usuario


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


def crear_sitio_seed(form):
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
    return nuevo

def crear_sitio(form):
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

    tag_ids = form.getlist("tags") # Obtener lista de IDs de tags
    if tag_ids:
        tags_seleccionados = db.session.query(Tag).filter(Tag.id.in_([_parse_int(tid) for tid in tag_ids])).all()
        nuevo.tags = tags_seleccionados

    db.session.add(nuevo)
    db.session.commit()
    return nuevo


def obtener_sitio(sitio_id: int):
    return db.session.get(SitioHistorico, sitio_id)


def editar_sitio(sitio_id: int, form):
    sitio = obtener_sitio(sitio_id)
    if not sitio:
        return False

    sitio.nombre = form.get("nombre") or sitio.nombre
    sitio.descBreve = form.get("descripcion") or sitio.descBreve
    sitio.descCompleta = form.get("descripcion_completa") or sitio.descCompleta
    sitio.idCiudad = _parse_int(form.get("ciudad")) or sitio.idCiudad
    sitio.idCategoria = _parse_int(form.get("categoria")) or sitio.idCategoria
    sitio.latitud = (
        _parse_float(form.get("latitud"))
        if form.get("latitud") is not None
        else sitio.latitud
    )
    sitio.longitud = (
        _parse_float(form.get("longitud"))
        if form.get("longitud") is not None
        else sitio.longitud
    )
    sitio.estadoConservacion = (
        form.get("estado_conservacion") or sitio.estadoConservacion
    )
    anio = _parse_date(form.get("fecha_inauguracion"))
    if anio:
        sitio.anioInauguracion = anio
    fecha_reg = _parse_date(form.get("fecha_registro"))
    if fecha_reg:
        sitio.fechaRegistro = fecha_reg
    if form.get("visible") is not None:
        sitio.visible = True if form.get("visible") in ("True", True) else False
    
    tag_ids = form.getlist("tags")
    # Buscar los objetos Tag correspondientes a los IDs seleccionados
    tags_seleccionados = db.session.query(Tag).filter(Tag.id.in_([_parse_int(tid) for tid in tag_ids])).all()
    # Asignar la nueva lista de tags. SQLAlchemy maneja la desvinculación de los anteriores.
    sitio.tags = tags_seleccionados

    db.session.commit()
    return True


def eliminar_sitio(sitio_id: int):
    sitio = obtener_sitio(sitio_id)
    if not sitio:
        return False
    sitio.baja = True
    db.session.commit()
    return True

def create_rol(nombre: str):
    from src.core.board.rol import Rol

    nuevo = Rol(nombre=nombre)
    db.session.add(nuevo)
    db.session.commit()
    return nuevo

def list_roles():
    from src.core.board.rol import Rol

    return db.session.query(Rol).order_by(Rol.id).all()
def listar_tags():
    return db.session.query(Tag).order_by(Tag.nombre).all()

def obtener_tag(tag_id: int):
    return db.session.get(Tag, tag_id)

def crear_tag(form):
    nombre_tag = form.get("nombre")
    if not nombre_tag:
        return None
    nuevo_tag = Tag(nombre=nombre_tag)
    db.session.add(nuevo_tag)
    db.session.commit()
    return nuevo_tag

def editar_tag(tag_id: int, form):
    tag = obtener_tag(tag_id)
    if not tag:
        return False
    
    nuevo_nombre = form.get("nombre")
    if nuevo_nombre and nuevo_nombre != tag.nombre:
        tag.nombre = nuevo_nombre
        db.session.commit()
        return True
    return False

def eliminar_tag(tag_id: int):
    tag = obtener_tag(tag_id)
    if not tag:
        return False
    # No se puede eliminar si hay sitios asociados (esto lo manejará la DB con restricciones)
    # Por simplicidad, asumimos que la relación muchos a muchos se limpia automáticamente
    # o que la BD tiene ON DELETE CASCADE. Aquí solo intentamos borrar el objeto.
    db.session.delete(tag)
    db.session.commit()
    return True
