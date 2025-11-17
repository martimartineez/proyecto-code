from src.core.entity import services
from src.core.entity.services import EntityNotFoundError
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
from src.core.auth import Usuario
from src.core.entity.sitio_historico import SitioHistorico
from src.core.database import db
from src.core.entity.ciudad import Ciudad
from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from sqlalchemy import or_
from src.core.entity.tag import Tag
from src.core.entity.validaciones import validar_sitio_historico
from src.web.handlers.auth import login_required, check_permission, check
from sqlalchemy import func
import io, csv
from flask import Response
from datetime import date, timezone, timedelta
import uuid, mimetypes, os
from werkzeug.utils import secure_filename



bp = Blueprint("sitios_historicos", __name__, url_prefix="/sitioshistoricos")

def _current_user_id() -> int | None:
    """Return authenticated user id. Prefer session['user_id']; fallback to email lookup for legacy sessions."""
    try:
        uid = session.get("user_id")
        if uid:
            return uid
        email = session.get("user")
        if not email:
            return None
        u = db.session.query(Usuario).filter(Usuario.email == email).first()
        return u.id if u else None
    except Exception:
        return None


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
    # Mostrar listas (ej: tags) como texto separado por comas
    try:
        from collections.abc import Iterable
        if isinstance(valor, list):
            # Si la lista es de strings, unirlas; si no, convertir cada item a str
            if len(valor) == 0:
                return "—"
            return ", ".join([str(v) for v in valor])
    except Exception:
        pass
    # valores fecha en iso string
    try:
        if isinstance(valor, str) and len(valor) >= 10 and valor[4] == "-" and valor[7] == "-":
            return valor[:16].replace("T", " ")
    except Exception:
        pass
    return str(valor)


try:
    APP_TZ = ZoneInfo("America/Argentina/Buenos_Aires")
except ZoneInfoNotFoundError:
    APP_TZ = timezone(timedelta(hours=-3))  # UTC-3 como reemplazo


def _to_local(dt: datetime | None) -> datetime | None:
    if not dt:
        return None
    # Si viene naive, asumir UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    try:
        return dt.astimezone(APP_TZ)
    except Exception:
        return dt


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

        fecha_local = _to_local(e.fechaAccion)
        fecha_str = fecha_local.strftime('%Y-%m-%d %H:%M') if fecha_local else ""
        items_view.append({
            "fecha": fecha_local,
            "usuario_id": e.idUsuario,
            "usuario": usuario_label or f"#{e.idUsuario}",
            "accion": e.accion,
            "cambios": cambios,
            "fecha_str": fecha_str,
        })
    return {
        "items": items_view,
        "total": historial["total"],
        "page": historial["page"],
        "per_page": historial["per_page"],
        "pages": historial["pages"],
    }


@bp.get("/nuevo")
@login_required
@check("site_create")
def agregar_sitio_get():
    """
    Renderiza el formulario para agregar un nuevo sitio histórico.
    Proporciona datos necesarios como provincias, ciudades, categorías y tags.
    """
    next_url = request.args.get("next", url_for("sitios_historicos.busqueda_avanzada"))
    hoy = date.today().strftime('%Y-%m-%d')
    provincias = services.listar_provincias()
    ciudades = services.listar_ciudades()
    categorias = services.listar_categorias()
    tags = services.listar_tags()
    return render_template(
        "sitios_historicos/formAgregar.html",
        provincias=provincias,
        ciudades=ciudades,
        categorias=categorias,
        tags=tags,
        next_url=next_url,
        today=hoy,
    )

@bp.post("/nuevo")
@login_required
@check("site_create")
def agregar_sitio_post():
    """
    Procesa el formulario para agregar un nuevo sitio histórico.
    Valida los datos y maneja errores, redirigiendo según corresponda.
    Maneja tanto errores de validación como excepciones durante la creación.
    """
    next_url = request.args.get("next", url_for("sitios_historicos.busqueda_avanzada"))
    errores = validar_sitio_historico(request.form)

    if errores:
        full_error_msg = " | ".join(errores.values())
        flash(f"Hubo errores de validación en el formulario: {full_error_msg}", "error")
        # To avoid code duplication, consider redirecting to the GET route
        return redirect(url_for("sitios_historicos.agregar_sitio_get", next=next_url))
    
    try:
        nombre_sitio = services.crear_sitio(request.form, id_usuario=_current_user_id())
        if nombre_sitio:
            # Usamos el nombre devuelto en el mensaje flash
            flash(f"El sitio histórico '{nombre_sitio.nombre}' ha sido agregado exitosamente.", "success")
        return redirect(url_for("sitios_historicos.busqueda_avanzada"))
    except Exception as e:
        flash(f"Ocurrió un error al intentar agregar el sitio: {e}.", "error")
        # Redirect on error to avoid resubmission issues
        return redirect(url_for("sitios_historicos.agregar_sitio_get", next=next_url))



@bp.get("/<int:sitio_id>/editar")
@login_required
@check("site_update")
def editar_sitio_get(sitio_id):
    """
    Renderiza el formulario para editar un sitio histórico existente.
    Carga los datos actuales del sitio y proporciona datos necesarios como provincias, ciudades, categorías, tags y historial.
    Maneja filtros para el historial y prepara la vista del historial.
    Maneja el caso donde el sitio no existe.
    """
    next_url = request.args.get("next", url_for("sitios_historicos.busqueda_avanzada"))
    hoy = date.today().strftime('%Y-%m-%d')
    sitio = services.obtener_sitio(sitio_id)
    if not sitio:
        flash("Sitio histórico no encontrado.", "error")
        return redirect(url_for("sitios_historicos.busqueda_avanzada"))
        # Filtros de historial
    usuario_id = request.args.get("usuario_id", type=int)
    accion = request.args.get("accion")
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
    page = request.args.get("page", default=1, type=int)
    historial = services.listar_historial_sitio(
        id_sitio=sitio_id,
        usuario_id=usuario_id,
        accion=accion,
        desde=desde,
        hasta=hasta,
        page=page,
        per_page=25,
    )
    provincias = services.listar_provincias()
    ciudades = services.listar_ciudades()
    categorias = services.listar_categorias()
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
    tags = services.listar_tags()
    # Cargar las imágenes del sitio
    imagenes = services.listar_imagenes_sitio(sitio_id)
    for img in imagenes:
        print(img.url_publica)
    return render_template(
        "sitios_historicos/formEditar.html",
        sitio=sitio,
        imagenes=imagenes,  # Pasar las imágenes a la plantilla
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
        today=hoy,
    )

@bp.post("/<int:sitio_id>/editar")
@login_required
@check("site_update")
def editar_sitio_post(sitio_id):
    """
    Procesa el formulario para editar un sitio histórico existente.
    Valida los datos y maneja errores, redirigiendo según corresponda.
    Maneja tanto errores de validación como excepciones durante la edición.
    Maneja el caso donde el sitio no existe.
    """
    next_url = request.args.get("next", url_for("sitios_historicos.busqueda_avanzada"))
    errores = validar_sitio_historico(request.form)
    
    if errores:
        full_error_msg = " | ".join(errores.values())
        flash(f"Hubo errores de validación en el formulario: {full_error_msg}", "error")
        return redirect(url_for("sitios_historicos.editar_sitio_get", sitio_id=sitio_id, next=next_url))
        
    try:
        nombre_sitio = services.editar_sitio(sitio_id, request.form, id_usuario=_current_user_id())
        if nombre_sitio:
            # Usamos el nombre devuelto en el mensaje flash
            flash(f"El sitio histórico '{nombre_sitio.nombre}' ha sido editado exitosamente.", "success")

        return redirect(url_for("sitios_historicos.busqueda_avanzada"))

    except EntityNotFoundError:
        # Captura la excepción de "no encontrado"
        flash("Error: El sitio histórico no fue encontrado para su edición.", "error")
        return redirect(url_for("sitios_historicos.busqueda_avanzada"))
    except Exception as e:
        flash(f"Ocurrió un error al intentar editar el sitio: {e}.", "error")
        return redirect(url_for("sitios_historicos.editar_sitio_get", sitio_id=sitio_id, next=next_url))


@bp.post("/<int:sitio_id>/eliminar")
@login_required
@check("site_destroy")
def eliminar_sitio(sitio_id):
    """
    Elimina un sitio histórico existente.
    Maneja excepciones durante la eliminación y proporciona retroalimentación al usuario.
    Maneja el caso donde el sitio no existe.
    Redirige a la página de búsqueda avanzada después de la operación.
    """
    try:
        # 💡 Capturamos el valor devuelto (el nombre del sitio o False)
        nombre_sitio = services.eliminar_sitio(sitio_id, id_usuario=_current_user_id()) 
        
        if nombre_sitio:
            # Usamos el nombre devuelto en el mensaje flash
            flash(f"El sitio histórico '{nombre_sitio.nombre}' ha sido eliminado exitosamente.", "success")

    except EntityNotFoundError:
        # Captura la excepción de "no encontrado"
        flash("Error: El sitio histórico que intentaste eliminar no fue encontrado.", "error")

    except Exception as e:
        flash(f"Ocurrió un error al intentar eliminar el sitio: {e}.", "error")
    
    return redirect(url_for("sitios_historicos.busqueda_avanzada"))

@bp.route("/sitio/<int:sitio_id>")
@login_required
@check("site_show")
def ver_sitio(sitio_id):
    """
    Muestra los detalles de un sitio histórico específico junto con su historial de cambios.
    Maneja filtros para el historial y prepara la vista del historial.
    Maneja el caso donde el sitio no existe.
    """
    next_url = request.args.get("next", url_for("sitios_historicos.busqueda_avanzada"))
    sitio = services.obtener_sitio(sitio_id)
    if not sitio:
        flash("Sitio histórico no encontrado.", "error")
        return redirect(url_for("sitios_historicos.busqueda_avanzada"))
    # Filtros de historial
    usuario_id = request.args.get("usuario_id", type=int)
    accion = request.args.get("accion")
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
    page = request.args.get("page", default=1, type=int)
    historial = services.listar_historial_sitio(
        id_sitio=sitio_id,
        usuario_id=usuario_id,
        accion=accion,
        desde=desde,
        hasta=hasta,
        page=page,
        per_page=25,
    )
    ciudades = services.listar_ciudades()
    categorias = services.listar_categorias()
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
        next_url=next_url,
    )

# ==============================
# Gestión de Imágenes (Privado)
# ==============================

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

def _allowed_file(filename: str) -> bool:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in ALLOWED_EXTENSIONS

def _build_public_url(app, object_name: str) -> str:
    server = app.config["MINIO_SERVER"]
    bucket = app.config["MINIO_BUCKET"]
    secure = app.config.get("MINIO_SECURE", False)
    scheme = "https" if secure else "http"
    return f"{scheme}://{server}/{bucket}/{object_name}"

def _put_object(client, bucket: str, object_name: str, file_storage) -> None:
    # Reset stream and determine length
    file_storage.stream.seek(0, os.SEEK_END)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)
    content_type = file_storage.mimetype or mimetypes.guess_type(file_storage.filename)[0] or "application/octet-stream"
    client.put_object(
        bucket,
        object_name,
        data=file_storage.stream,
        length=size,
        content_type=content_type,
    )

@bp.post("/<int:sitio_id>/imagenes")
@login_required
@check("site_update")
def subir_imagenes_sitio(sitio_id: int):
    """Sube múltiples imágenes para un sitio con validaciones y registra en DB."""
    app = current_app
    client = app.storage
    bucket = app.config["MINIO_BUCKET"]

    # Validar cantidad total
    total_actual = services.contar_imagenes_sitio(sitio_id)
    files = request.files.getlist("imagenes") or []
    metas = request.form  # titulo_alt_i, desc_i, portada_index opcional
    if not files:
        flash("No se seleccionaron archivos.", "error")
        return redirect(url_for("sitios_historicos.editar_sitio_get", sitio_id=sitio_id))
    if total_actual + len(files) > 10:
        flash("Límite de 10 imágenes por sitio excedido.", "error")
        return redirect(url_for("sitios_historicos.editar_sitio_get", sitio_id=sitio_id))

    portada_index = metas.get("portada_index")
    created = 0
    errors = []

    for idx, f in enumerate(files):
        if not f or f.filename == "":
            errors.append(f"Archivo #{idx+1} inválido")
            continue
        filename = secure_filename(f.filename)
        if not _allowed_file(filename):
            errors.append(f"Formato no permitido para {filename}. Use JPG, PNG o WEBP.")
            continue
        # tamaño
        f.stream.seek(0, os.SEEK_END)
        size = f.stream.tell()
        f.stream.seek(0)
        if size > MAX_FILE_SIZE:
            errors.append(f"{filename}: supera 5 MB")
            continue

        ext = filename.rsplit(".", 1)[-1].lower()
        object_name = f"public/{sitio_id}/{uuid.uuid4().hex}.{ext}"
        try:
            _put_object(client, bucket, object_name, f)
            url_publica = _build_public_url(app, object_name)
            titulo_alt = metas.get(f"titulo_alt_{idx}") or filename
            if not titulo_alt:
                errors.append(f"{filename}: título/alt es obligatorio")
                continue
            descripcion = metas.get(f"descripcion_{idx}")
            es_portada = str(idx) == str(portada_index) if portada_index is not None else False
            services.agregar_imagen_sitio(
                id_sitio=sitio_id,
                url_publica=url_publica,
                object_name=object_name,
                titulo_alt=titulo_alt,
                descripcion=descripcion,
                es_portada=es_portada,
            )
            created += 1
        except Exception as e:
            errors.append(f"{filename}: {e}")

    if created:
        flash(f"{created} imagen(es) subida(s) correctamente.", "success")
    if errors:
        flash(" | ".join(errors), "error")
    return redirect(url_for("sitios_historicos.editar_sitio_get", sitio_id=sitio_id))

# Reemplaza estas rutas en tu sitios_historicos.py
# Cambia los decoradores @bp.post a @bp.route con methods

@bp.route("/<int:sitio_id>/imagenes/<int:imagen_id>/portada", methods=["GET", "POST"])
@login_required
@check("site_update")
def set_portada(sitio_id: int, imagen_id: int):
    try:
        services.set_portada_imagen(sitio_id, imagen_id)
        flash("Portada actualizada.", "success")
    except EntityNotFoundError:
        flash("Imagen no encontrada para el sitio.", "error")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("sitios_historicos.editar_sitio_get", sitio_id=sitio_id))

@bp.route("/<int:sitio_id>/imagenes/<int:imagen_id>/eliminar", methods=["GET", "POST"])
@login_required
@check("site_update")
def eliminar_imagen(sitio_id: int, imagen_id: int):
    app = current_app
    client = app.storage
    bucket = app.config["MINIO_BUCKET"]
    try:
        img = services.obtener_imagen(imagen_id)
        if not img or img.id_sitio != sitio_id:
            raise EntityNotFoundError("Imagen no encontrada.")
        object_name = img.object_name
        services.eliminar_imagen_sitio(sitio_id, imagen_id)
        # Borrar del storage (ignorar error si no existe)
        try:
            client.remove_object(bucket, object_name)
        except Exception:
            pass
        flash("Imagen eliminada.", "success")
    except ValueError as ve:
        flash(str(ve), "error")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("sitios_historicos.editar_sitio_get", sitio_id=sitio_id))

# Para actualizar datos, debe ser POST
@bp.route("/<int:sitio_id>/imagenes/<int:imagen_id>/actualizar", methods=["POST"])
@login_required
@check("site_update")
def actualizar_data_imagen(sitio_id: int, imagen_id: int):
    try:
        titulo_alt = request.form.get("titulo_alt", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        
        if not titulo_alt:
            return jsonify({"error": "El título/alt es obligatorio."}), 400
        
        services.actualizar_data_imagen(sitio_id, imagen_id, titulo_alt, descripcion)
        return jsonify({"success": True, "message": "Datos actualizados"}), 200
    except EntityNotFoundError:
        return jsonify({"error": "Imagen no encontrada."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.post("/<int:sitio_id>/imagenes/orden")
@login_required
@check("site_update")
def reordenar_imagenes(sitio_id: int):
    try:
        ids = request.form.getlist("ids")  # e.g., ["3","1","2"]
        ids = [int(x) for x in ids]
        services.reordenar_imagenes_sitio(sitio_id, ids)
        flash("Orden actualizado.", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("sitios_historicos.editar_sitio_get", sitio_id=sitio_id))



def filtrar(filtros):
    provincia_id = filtros.get("provincia")
    ciudad_id = filtros.get("ciudad")
    categoria_id = filtros.get("categoria")
    estado_conservacion = filtros.get("estado_conservacion")
    fecha_desde = filtros.get("fecha_desde")
    fecha_hasta = filtros.get("fecha_hasta")
    visibilidad = filtros.get("visibilidad")
    sort_by = filtros.get("sort_by", "fecha_registro")
    order = filtros.get("order", "asc")
    tag_ids = filtros.get("tags", [])

    query = db.session.query(SitioHistorico).join(Ciudad)

    buscar = (filtros.get("buscar") or "").strip()
    if tag_ids:
        query = query.join(SitioHistorico.tags).filter(Tag.id.in_(tag_ids))
        query = query.group_by(SitioHistorico.id)
        query = query.having(func.count(Tag.id) == len(tag_ids))

    if provincia_id:
        query = query.filter(Ciudad.idProvincia == provincia_id)
    if ciudad_id:
        query = query.filter(SitioHistorico.idCiudad == ciudad_id)
    if categoria_id:
        query = query.filter(SitioHistorico.idCategoria == categoria_id)
    if estado_conservacion:
        query = query.filter(SitioHistorico.estadoConservacion.ilike(f"%{estado_conservacion}%"))
    if fecha_desde:
        query = query.filter(SitioHistorico.fechaRegistro >= fecha_desde)
    if fecha_hasta:
        query = query.filter(SitioHistorico.fechaRegistro <= fecha_hasta)
    if visibilidad == "1":
        query = query.filter(SitioHistorico.visible == True)
    elif visibilidad == "0":
        query = query.filter(SitioHistorico.visible == False)
    if buscar:
        from sqlalchemy import or_
        query = query.filter(
            or_(
                SitioHistorico.nombre.ilike(f"%{buscar}%"),
                SitioHistorico.descBreve.ilike(f"%{buscar}%")
            )
        )
    query = query.filter(SitioHistorico.baja == False)
    
    valid_sort_columns = {
        "fecha_registro": SitioHistorico.fechaRegistro,
        "nombre": SitioHistorico.nombre,
        "ciudad": Ciudad.nombre,
    }
    column = valid_sort_columns.get(sort_by, SitioHistorico.fechaRegistro)
    query = query if sort_by == "ciudad" else query
    query = query.order_by(column.desc() if order == "desc" else column.asc())

    return query


@bp.route("/", methods=["GET"])
@login_required
@check("site_index")
def busqueda_avanzada():
    """
    Muestra la página de búsqueda avanzada de sitios históricos con múltiples filtros.
    Permite filtrar por provincia, ciudad, categoría, estado de conservación, fechas, visibilidad y tags.
    Soporta paginación y ordenamiento de resultados.
    Proporciona un enlace para exportar los resultados filtrados a CSV.
    """
    provincias = services.listar_provincias()
    ciudades = services.listar_ciudades()
    categorias = services.listar_categorias()
    tags = services.listar_tags()


    per_page = 25
    page = request.args.get("page", 1, type=int)

    filtros = {
    "provincia": request.args.get("provincia"),
    "ciudad": request.args.get("ciudad"),
    "categoria": request.args.get("categoria"),
    "estado_conservacion": request.args.get("estado_conservacion"),
    "fecha_desde": request.args.get("fecha_desde"),
    "fecha_hasta": request.args.get("fecha_hasta"),
    "visibilidad": request.args.get("visibilidad"),
    "sort_by": request.args.get("sort_by"),
    "order": request.args.get("order"),
    "tags": request.args.getlist("tags", type=int),
    "buscar": request.args.get("buscar"),
}
    query = filtrar(filtros);
    
    total_results = query.count()
    total_pages = (total_results + per_page - 1) // per_page
    sitios = query.offset((page - 1) * per_page).limit(per_page).all()


    return render_template(
        "sitios_historicos/busquedaAvanzada.html",
        provincias=provincias,
        ciudades=ciudades,
        categorias=categorias,
        sitios=sitios,
        page=page,
        total_pages=total_pages,
        total_results=total_results,
        request_args=request.args,
        tags=tags,
        date=date
    )


@bp.route("/exportar_csv")
@login_required
@check("site_export")
def exportar_csv():
    """
    Exporta los resultados filtrados de la búsqueda avanzada de sitios históricos a un archivo CSV.
    Aplica los mismos filtros que la búsqueda avanzada y genera un archivo CSV descargable.
    """
    
    sitios = filtrar(request).all()

    data = []
    for s in sitios:
        data.append({
            "Nombre": s.nombre,
            "Descripcion": s.descBreve or "",
            "Ciudad": s.ciudad.nombre if s.ciudad else "",
            "Provincia": s.ciudad.provincia.nombre if s.ciudad and s.ciudad.provincia else "",
            "Estado": s.estadoConservacion or "",
            "FechaRegistro": s.fechaRegistro.strftime("%Y-%m-%d"),
            "Coordenadas": f"{s.latitud}, {s.longitud}" if s.latitud and s.longitud else "",
            "Tags": ", ".join([t.nombre for t in s.tags])
        })
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"sitios_{timestamp}.csv"


    output = io.StringIO()
    fieldnames = ["Nombre", "Descripcion", "Ciudad", "Provincia", "Estado", "FechaRegistro", "Coordenadas", "Tags"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )