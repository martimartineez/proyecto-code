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
    """
    Intenta convertir un valor a float. Retorna None si no es posible.
    """
    try:
        return float(value) if value not in (None, "") else None
    except Exception:
        return None


def _parse_int(value):
    """
    Intenta convertir un valor a int. Retorna None si no es posible.
    """
    try:
        return int(value) if value not in (None, "") else None
    except Exception:
        return None


def _parse_date(value):
    """
    Intenta convertir un valor a date (YYYY-MM-DD). Retorna None si no es posible.
    """
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
    """
    Lista los sitios historicos con paginacion.
    """
    return (
        db.session.query(SitioHistorico)
        .order_by(SitioHistorico.id)
        .filter_by(baja=False)
        .limit(per_page)
        .offset((page - 1) * per_page)
        .all()
    )

def contar_sitios():
    """
    Cuenta los sitios historicos activos (baja=False).
    """
    return db.session.query(SitioHistorico).filter_by(baja=False).count()

def listar_provincias():
    """
    Lista todas las provincias ordenadas por nombre.
    """
    return db.session.query(Provincia).order_by(Provincia.nombre).all()


def listar_ciudades(id_provincia: int | None = None):
    """
    Lista todas las ciudades, o las de una provincia específica si se proporciona id_provincia.
    """
    q = db.session.query(Ciudad)
    if id_provincia is not None:
        q = q.filter(Ciudad.idProvincia == id_provincia)
    return q.order_by(Ciudad.nombre).all()


def listar_categorias():
    """
    Lista todas las categorias de sitios ordenadas por nombre.
    """
    return db.session.query(CategoriaSitio).order_by(CategoriaSitio.nombre).all()


def crear_sitio_seed(form):
    """
    creacion de sitio historico, usado solo para pruebas de los desarrolladores.
    """
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
    """
    Creacion de sitio historico, usado en el blueprint de sitios.
    A partir de los datos del formulario.
    Reflejando los cambios en el historial.
    """
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
        visible=True,
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
    """
    Obtiene un sitio historico por su ID.
    """
    return db.session.get(SitioHistorico, sitio_id)


def editar_sitio(sitio_id: int, form, id_usuario: int | None = None):
    """
    Edicion de sitio historico, usado en el blueprint de sitios.
    A partir de los datos del formulario.
    Reflejando los cambios en el historial.
    """
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
        # Determinar acción específica: si cambiaron los tags => TAGS_CHANGED, si no => UPDATED
        accion_evento = "TAGS_CHANGED" if prev.get("tags") != nuevos.get("tags") else "UPDATED"
        registrar_evento_historial(
            id_sitio=sitio.id,
            id_usuario=id_usuario,
            accion=accion_evento,
            valores_anteriores=prev,
            valores_nuevos=nuevos,
        )
    except Exception:
        db.session.rollback()
    return sitio


def eliminar_sitio(sitio_id: int, id_usuario: int | None = None):
    """
    Realiza la eliminacion logica de un sitio historico (establece 'baja' en True).
    Reflejando los cambios en el historial.
    """
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
        # Unificamos en UPDATED para no exponer acciones 'STATE_CHANGED' o 'DELETED' en el filtro
        registrar_evento_historial(
            id_sitio=sitio.id,
            id_usuario=id_usuario,
            accion="UPDATED",
            valores_anteriores={"baja": prev_baja},
            valores_nuevos={"baja": sitio.baja},
        )
    except Exception:
        db.session.rollback()
        raise
    #si todo salio bien retorno el nombre del sitio eliminado
    return sitio


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
    """
    Lista los tags con paginacion, busqueda y ordenamiento.
    """
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
    """
    Cuenta los tags activos (baja=False), con filtro de búsqueda opcional.
    """
    query = db.session.query(Tag)

    #Filtro excluir Tags con baja=True
    query = query.filter(Tag.baja == False) 

    if q:
        query = query.filter(Tag.nombre.ilike(f"%{q}%"))
    return query.count()



def obtener_tag(tag_id: int):
    """
    Obtiene un tag por su ID.
    """
    return db.session.get(Tag, tag_id)


def obtener_tag_existente_por_nombre(nombre_tag: str):
    """
    Busca un tag existente (activo o dado de baja) por nombre.
    Retorna el Tag o None.
    """
    if not nombre_tag:
        return None
    
    return db.session.query(Tag).filter(Tag.nombre == nombre_tag).first()


def procesar_o_crear_tag(nombre_tag: str):
    """
    1. Revisa duplicados/tags dados de baja.
    2. Reactiva si es baja=True.
    3. Si no existe, lo crea.
    Retorna: Tag si es creado/reactivado.
    Lanza: IntegrityError si el nombre existe y está activo.
    """
    existing_tag = obtener_tag_existente_por_nombre(nombre_tag)

    if existing_tag:
        if existing_tag.baja:
            # Re-activar y retornar el tag existente
            existing_tag.baja = False
            existing_tag.slug = _generate_slug(nombre_tag) 
            db.session.commit()
            return existing_tag
        else:
            # El tag existe y está activo -> Lanzar excepción de duplicidad
            raise IntegrityError("Tag ya existe", params={}, orig=None)

    # El tag no existe, se crea
    slug_tag = _generate_slug(nombre_tag)
    return crear_tag(nombre_tag=nombre_tag, slug_tag=slug_tag)


def crear_tag(nombre_tag: str, slug_tag: str):
    """
    Creación simple de tag. Asume que la validación de duplicados ya se hizo.
    Se utiliza solo si el tag NO existe.
    Retorna: el Tag creado/modificado.
    """
    nuevo_tag = Tag(nombre=nombre_tag, slug=slug_tag) 
    db.session.add(nuevo_tag)
    db.session.commit()
    return nuevo_tag


def editar_tag(tag_id: int, nombre_nuevo: str):
    """
    Edita un tag existente.
    
    Lanza: 
        - IntegrityError si el nombre_nuevo ya existe en la DB (UNIQUE constraint).
        - Exception si el commit falla por otra razón (se propaga).
    
    Retorna: El objeto Tag editado.
    """
    tag = obtener_tag(tag_id)
    if not tag:
        return None 
    
    # Asignar nuevos valores.
    tag.nombre = nombre_nuevo
    tag.slug = _generate_slug(nombre_nuevo)
    
    # Intentar el commit. Si el nombre ya existe, la DB lanza IntegrityError.
    db.session.commit()
    return tag

def editar_tag(tag_id: int, form):
    """
    Edicion de tag, usado en el blueprint de tags.
    A partir de los datos del formulario.
    Maneja duplicados.
    Retorna: True (éxito), "DUPLICATE_ERROR" (si ya existe otro tag con el nuevo nombre), False (Tag no encontrado o error inesperado).
    """
    tag = obtener_tag(tag_id)
    if not tag:
        return False
    
    nuevo_nombre = form.get("nombre")
    if not nuevo_nombre:
        return False # o manejar error de nombre vacío

    # 1. Actualizar el Tag con el nuevo nombre y slug
    # Si el nombre NO CAMBIA, no hay problema de unicidad.
    # Si el nombre CAMBIA y ya existe en otro Tag, el IntegrityError se lanzará en el commit.
    tag.nombre = nuevo_nombre
    tag.slug = _generate_slug(nuevo_nombre) 
    
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


# clase para manejar el error de tag vinculado a sitios
class TagVinculadoError(Exception):
    def __init__(self, sitios_vinculados, message="El tag está asociado a sitios activos."):
        self.sitios_vinculados = sitios_vinculados
        super().__init__(message)

def eliminar_tag(tag_id: int):
    """
    Realiza la eliminación lógica de un Tag (establece 'baja' en True).
    Retorna: True (éxito), "vinculado" (error por vínculos), False (Tag no encontrado).
    """
    tag = obtener_tag(tag_id)
    if not tag:
        return True  # Si no existe, consideramos que ya está "eliminado"
    
    # 1. VERIFICAR VÍNCULOS CON SITIOS ACTIVOS
    sitios_vinculados = db.session.query(SitioHistorico.nombre).join(
        Tag.sitios
    ).filter(
        Tag.id == tag_id,
        SitioHistorico.baja == False  # Solo sitios activos
    ).all()

    if sitios_vinculados:
        # Lanzar excepción con la lista de nombres
        nombres = [s[0] for s in sitios_vinculados]
        raise TagVinculadoError(nombres, "El Tag no puede ser eliminado. Está asociado a sitios activos.")

    # 2. PROCEDER CON LA ELIMINACIÓN LÓGICA
    try:
        tag.baja = True
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        # Lanza cualquier otro error de DB
        raise

def create_rol(nombre: str):
    from src.core.board.rol import Rol

    nuevo = Rol(nombre=nombre)
    db.session.add(nuevo)
    db.session.commit()
    return nuevo

def list_roles():
    from src.core.board.rol import Rol

    return db.session.query(Rol).order_by(Rol.id).all()

def get_rol_by_id(rol_id: int):
    from src.core.board.rol import Rol

    return db.session.get(Rol, rol_id)

def get_id_rol_admin():
    from src.core.board.rol import Rol

    rol_admin = db.session.query(Rol).filter(Rol.nombre == "Admin").first()
    return rol_admin.id if rol_admin else None


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
