from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from src.core.database import db
from src.core.board.sitio_historico import SitioHistorico
from src.core.board.historial_sitio import HistorialSitio
from src.core.board.provincia import Provincia
from src.core.board.ciudad import Ciudad
from src.core.board.categoria_sitio import CategoriaSitio  # noqa: F401
from src.core.board.tag import Tag  # noqa: F401
from src.core.auth.usuario import Usuario
import re

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

def _generate_slug(text: str) -> str:
    """
    Genera un slug a partir de un texto usando solo librerías estándar.
    Maneja tildes y 'ñ' mediante reemplazo manual.
    """
    # 1. Mapeo de caracteres especiales a sus equivalentes sin acento
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n', 'ü': 'u',
        'Á': 'a', 'É': 'e', 'Í': 'i', 'Ó': 'o', 'Ú': 'u', 'Ñ': 'n', 'Ü': 'u',
    }
    
    # 2. Aplicar mapeo y convertir a minúsculas
    text = text.lower()
    for old, new in replacements.items():
        text = text.replace(old, new)

    # 3. Reemplazar caracteres no deseados (excepto a-z, 0-9 y guiones) con un guion.
    # Esto también manejará los espacios.
    text = re.sub(r'[^a-z0-9\-]+', '-', text) 
    
    # 4. Eliminar guiones duplicados (ej: 'sitio--historico' -> 'sitio-historico')
    text = re.sub(r'-+', '-', text)
    
    # 5. Eliminar guiones al inicio y al final de la cadena
    text = text.strip('-')
    
    return text

def listar_sitios(page=1, per_page=25):
    return (
        db.session.query(SitioHistorico)
        .order_by(SitioHistorico.id)
        .filter_by(baja=False)
        .limit(per_page)
        .offset((page - 1) * per_page)
        .all()
    )

def contar_sitios():
    return db.session.query(SitioHistorico).filter_by(baja=False).count()

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
        # Manejar hidden + checkbox (dos valores). True si cualquiera es truthy
        visible=(
            any(
                str(v).lower() in ("true", "1", "yes", "on", "t")
                for v in form.getlist("visible")
            )
        ),
        baja=False,
    )

    tag_ids = form.getlist("tags") # Obtener lista de IDs de tags
    if tag_ids:
        tags_seleccionados = db.session.query(Tag).filter(Tag.id.in_([_parse_int(tid) for tid in tag_ids])).all()
        nuevo.tags = tags_seleccionados

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
                "tags": [t.nombre for t in getattr(nuevo, "tags", [])],
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
        # Snapshot de tags como lista de nombres para facilitar la visualización
        "tags": [t.nombre for t in getattr(sitio, "tags", [])],
    }

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
    # Checkbox HTML + hidden: se reciben 0, 1 o 2 valores. True si cualquiera es truthy
    vals_visible = form.getlist("visible")
    sitio.visible = any(str(v).lower() in ("true", "1", "yes", "on", "t") for v in vals_visible)
    
    tag_ids = form.getlist("tags")
    # Buscar los objetos Tag correspondientes a los IDs seleccionados
    tags_seleccionados = db.session.query(Tag).filter(Tag.id.in_([_parse_int(tid) for tid in tag_ids])).all()
    # Asignar la nueva lista de tags. SQLAlchemy maneja la desvinculación de los anteriores.
    sitio.tags = tags_seleccionados

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
        "tags": [t.nombre for t in getattr(sitio, "tags", [])],
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
def listar_tags(page=1, per_page=25, q=None, sort=None, order="asc"):
    query = db.session.query(Tag)

    #Filtro excluir Tags con baja=True
    query = query.filter(Tag.baja == False) 

    # Filtro de búsqueda
    if q:
        query = query.filter(Tag.nombre.ilike(f"%{q}%"))
    
    

    # Armamos lista de criterios de orden
    order_by_list = []
    if sort:
        for criterio in sort.split(","):  # Ej: "nombre,fecha"
            if criterio == "nombre":
                column = Tag.nombre
            elif criterio == "fecha":
                column = Tag.inserted_at
            else:
                continue

            if order == "desc":
                order_by_list.append(column.desc())
            else:
                order_by_list.append(column.asc())

    # Si no hay sort, por defecto nombre asc
    if not order_by_list:
        order_by_list = [Tag.nombre.asc()]

    query = query.order_by(*order_by_list)

    return query.limit(per_page).offset((page - 1) * per_page).all()


def contar_tags(q=None):
    query = db.session.query(Tag)

    #Filtro excluir Tags con baja=True
    query = query.filter(Tag.baja == False) 

    if q:
        query = query.filter(Tag.nombre.ilike(f"%{q}%"))
    return query.count()



def obtener_tag(tag_id: int):
    return db.session.get(Tag, tag_id)

# En src/core/board/__init__.py
# NOTA IMPORTANTE: Asegúrate de que la importación de IntegrityError sea de SQLAlchemy,
# no de sqlite3, como hicimos en la corrección anterior:
# from sqlalchemy.exc import IntegrityError 

def crear_tag(form):
    nombre_tag = form.get("nombre")
    if not nombre_tag:
        return None
    
    # 1. Verificar si ya existe un Tag con este nombre (activo o borrado lógicamente).
    existing_tag = db.session.query(Tag).filter(
        Tag.nombre == nombre_tag
    ).first()
    
    if existing_tag:
        if existing_tag.baja:
            # El Tag existe, pero está dado de BAJA. Lo RE-ACTIVAMOS.
            existing_tag.baja = False
            # Opcional: Re-generar el slug por si la lógica de slug cambia
            existing_tag.slug = _generate_slug(nombre_tag) 
            try:
                db.session.commit()
                return existing_tag
            except IntegrityError:
                # Esto es un fallback, si por alguna razón el re-commit falla
                db.session.rollback()
                return "DUPLICATE_ERROR"
            except Exception:
                db.session.rollback()
                return None
        else:
            # El Tag existe y está ACTIVO. Es un duplicado.
            return "DUPLICATE_ERROR" 

    # GENERACIÓN DEL SLUG (solo si es un Tag completamente nuevo)
    slug_tag = _generate_slug(nombre_tag)
    
    nuevo_tag = Tag(nombre=nombre_tag, slug=slug_tag) 
    db.session.add(nuevo_tag)
    try:
        db.session.commit()
        return nuevo_tag
    except IntegrityError:
        # Fallback si el nombre/slug es un duplicado que no se encontró en la consulta previa
        db.session.rollback()
        return "DUPLICATE_ERROR"
    except Exception:
        # Otros errores de base de datos
        db.session.rollback()
        return None

def editar_tag(tag_id: int, form):
    tag = obtener_tag(tag_id)
    if not tag:
        return False
    
    nuevo_nombre = form.get("nombre")
    if not nuevo_nombre:
        return False # o manejar error de nombre vacío

    # 1. Actualizar el Tag con el nuevo nombre y slug
    # Esto es crucial: Si el nombre NO CAMBIA, no hay problema de unicidad.
    # Si el nombre CAMBIA y ya existe en otro Tag, el IntegrityError se lanzará en el commit.
    tag.nombre = nuevo_nombre
    tag.slug = _generate_slug(nuevo_nombre) # Asumo que actualizas el slug también
    
    try:
        db.session.commit()
        return True # Éxito
    except IntegrityError:
        # ⚠️ ERROR ESPECÍFICO DE DUPLICIDAD (el nuevo nombre o slug ya existe en OTRO tag)
        db.session.rollback()
        # Retornamos la cadena específica para que el blueprint lo sepa
        return "DUPLICATE_ERROR" 
    except Exception:
        # Otros errores de base de datos
        db.session.rollback()
        return None


def eliminar_tag(tag_id: int):
    """
    Realiza la eliminación lógica de un Tag (establece 'baja' en True).
    Retorna: True (éxito), "vinculado" (error por vínculos), False (Tag no encontrado).
    """
    tag = obtener_tag(tag_id)
    if not tag:
        return False
    
    
    # Verificar SOLO asociaciones con sitios ACTIVOS
    
    from src.core.board.sitio_historico import SitioHistorico 
    
    # 1. VERIFICACIÓN DE VINCULACIÓN: Buscar solo Sitios Históricos ACTIVOS (baja=False).
    # Utilizamos un JOIN para obtener los nombres de los Sitios Históricos vinculados.
    sitios_vinculados = db.session.query(SitioHistorico.nombre).join(
        Tag.sitios
    ).filter(
        Tag.id == tag_id,
        SitioHistorico.baja == False  # <--- ¡ESTE ES EL FILTRO CLAVE!
    ).all()

    if sitios_vinculados:
        # El Tag está asociado a sitios ACTIVOS. Retornamos la lista de nombres.
        nombres = [s[0] for s in sitios_vinculados]
        return nombres # Retorna la lista de nombres, e.g., ['Sitio A', 'Sitio B']

    # 2. PROCEDER CON LA ELIMINACIÓN LÓGICA (si no hay vinculación ACTIVA)
    try:
        tag.baja = True
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False

def create_rol(nombre: str):
    from src.core.board.rol import Rol

    nuevo = Rol(nombre=nombre)
    db.session.add(nuevo)
    db.session.commit()
    return nuevo

def list_roles():
    from src.core.board.rol import Rol

    return db.session.query(Rol).order_by(Rol.id).all()

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
