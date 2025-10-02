from datetime import datetime
from src.core.database import db
from src.core.board.sitio_historico import SitioHistorico
from src.core.board.provincia import Provincia
from src.core.board.ciudad import Ciudad
from src.core.board.categoria_sitio import CategoriaSitio  # noqa: F401
from src.core.board.tag import Tag  # noqa: F401
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

def crear_tag(form):
    nombre_tag = form.get("nombre")
    if not nombre_tag:
        return None
    
    # GENERACIÓN DEL SLUG
    slug_tag = _generate_slug(nombre_tag)
    # NOTA: Deberías implementar aquí la lógica para asegurar que el slug sea único
    # si ya existe (ej: consultar la DB y si existe, generar 'slug-1', 'slug-2', etc.)
    
    nuevo_tag = Tag(nombre=nombre_tag, slug=slug_tag) # <--- Asignar el slug
    db.session.add(nuevo_tag)
    try:
        db.session.commit()
        return nuevo_tag
    except Exception:
        db.session.rollback()
        return None

def editar_tag(tag_id: int, form):
    tag = obtener_tag(tag_id)
    if not tag:
        return False
    
    nuevo_nombre = form.get("nombre")
    if nuevo_nombre and nuevo_nombre != tag.nombre:
        tag.nombre = nuevo_nombre
        
        # REGENERACIÓN DEL SLUG si el nombre cambia
        tag.slug = _generate_slug(nuevo_nombre) # <--- REGENERAR SLUG
        
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
            
    return True

# ... (dentro de __init__.py) ...

def eliminar_tag(tag_id: int):
    """
    Realiza la eliminación lógica de un Tag (establece 'baja' en True).
    Retorna: True (éxito), "vinculado" (error por vínculos), False (Tag no encontrado).
    """
    tag = obtener_tag(tag_id)
    if not tag:
        return False
    
    # OPCIONAL: Si quieres impedir la eliminación lógica mientras esté en uso:
    if len(tag.sitios) > 0:
        return "vinculado"
    
    # ELIMINACIÓN LÓGICA: Actualizar el campo 'baja'
    tag.baja = True
    db.session.commit()
    return True 

# ...
