from src.core.entity import services
from src.core.entity.services import TagVinculadoError, EntityNotFoundError
from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.web.handlers.auth import login_required, check
from src.core.entity.validaciones import validar_tag
from sqlalchemy.exc import IntegrityError
from src.core.database import db

bp = Blueprint("tags", __name__, url_prefix="/tags")


@bp.get("/")
@login_required
@check("tag_index")
def index():
    """
    Lista los tags con paginación, búsqueda y ordenamiento.
    """
    page = request.args.get("page", 1, type=int)
    per_page = 25
    q = request.args.get("q", None)
    sort = request.args.get("sort", "nombre")  # puede ser "nombre,fecha"
    order = request.args.get("order", "asc")

    tags = services.listar_tags(page=page, per_page=per_page, q=q, sort=sort, order=order)
    total = services.contar_tags(q=q)
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        "tags/index_tags.html",
        tags=tags,
        page=page,
        total_pages=total_pages,
        q=q,
        sort=sort,
        order=order
    )

@bp.get("/nuevo")
@login_required
@check("tag_create")
def agregar_tag_get():
    """
    Renderiza el formulario para agregar un nuevo tag."""
    return render_template("tags/form_tags.html", action="agregar")

@bp.post("/nuevo")
@login_required
@check("tag_create")
def agregar_tag_post():
    """
    Procesa el formulario para agregar un nuevo tag.
    Maneja validaciones y muestra mensajes flash según el resultado.
    """
    # Validar datos con la capa separada
    nombre_tag = request.form.get("nombre")
    errores = validar_tag(request.form)
    
    if errores:
        #1. Mostrar errores en flash messages y re-renderizar
        for campo, msg in errores.items():
            flash(f"{msg}", "error")
        # Devolver el formulario con los datos ingresados
        return render_template("tags/form_tags.html", action="agregar", form_data=request.form), 400
    
    try:
        # 2. Llamar a la lógica de negocio simple
        tag_creado = services.procesar_o_crear_tag(nombre_tag) 
        
        # 3. Éxito: retorna la entidad (Tag)
        if tag_creado:
            flash("Tag agregado exitosamente.", "success")
            return redirect(url_for("tags.index"))
        else:
            # Esto NO DEBERÍA pasar con la lógica de procesar_o_crear_tag
            flash("Ocurrió un error inesperado al intentar agregar el Tag.", "error")
            
    except IntegrityError:
        # 4. Error de duplicidad (activo)
        db.session.rollback() # Asegurar que la sesión se limpia
        flash(f"Error: Ya existe un Tag con el nombre '{nombre_tag}'.", "error")
        
    except Exception as e:
        # 5. Otro error de DB o inesperado
        db.session.rollback()
        flash(f"Ocurrió un error inesperado en el servidor: {e}", "error")
        
    # Si falló (duplicado o error), se vuelve a renderizar el formulario
    return render_template("tags/form_tags.html", action="agregar", form_data=request.form)




@bp.get("/<int:tag_id>/editar")
@login_required
@check("tag_update")
def editar_tag_get(tag_id):
    """
    Renderiza el formulario para editar un tag existente.
    Maneja el caso donde el tag no existe.
    """
    tag = services.obtener_tag(tag_id)
    if not tag:
        flash("Tag no encontrado.", "error")
        return redirect(url_for("tags.index"))
    # Renderiza el formulario con los datos del tag
    return render_template("tags/form_tags.html", tag=tag, action="editar")

@bp.post("/<int:tag_id>/editar")
@login_required
@check("tag_update")
def editar_tag_post(tag_id):
    """
    Procesa el formulario para editar un tag existente.
    Maneja validaciones y muestra mensajes flash según el resultado.
    """
    tag = services.obtener_tag(tag_id)
    if not tag:
        flash("Tag no encontrado.", "error")
        return redirect(url_for("tags.index"))

    # Validar datos con la capa separada
    errores = validar_tag(request.form)
    
    if errores:
        # Mostrar errores y re-renderizar
        for campo, msg in errores.items():
            flash(f"{msg}", "error")
        # Devolver el formulario con el tag existente y los datos POST
        return render_template("tags/form_tags.html", tag=tag, action="editar", form_data=request.form), 400

    nombre_nuevo = request.form.get("nombre")
    
    try:
        # La función solo hace la edición o lanza excepción
        services.editar_tag(tag.id, nombre_nuevo) 
        
        # 1. Éxito:
        flash("Tag editado exitosamente.", "success")
        return redirect(url_for("tags.index"))

    except IntegrityError:
        # 2. Falla: Duplicado (capturado por la excepción)
        db.session.rollback() # Limpiar la sesión si la excepción vino de la DB
        flash(f"Error: El nombre '{nombre_nuevo}' ya está siendo usado por otro tag activo.", "error")

    except Exception as e:
        # 3. Falla: Cualquier otro error inesperado
        db.session.rollback()
        flash(f"Ocurrió un error inesperado: {e}", "error")
        
    # Si falló (duplicado o error), se vuelve a renderizar el formulario
    return render_template("tags/form_tags.html", tag=tag, action="editar", form_data=request.form)



@bp.post("/<int:tag_id>/eliminar")
@login_required
@check("tag_destroy")
def eliminar_tag(tag_id):
    """
    Elimina un tag existente.
    Maneja el caso donde el tag no existe y muestra mensajes flash según el resultado.
    """
    try:
        # 1. Llama a la lógica de negocio (elimina o lanza error)
        services.eliminar_tag(tag_id)
        
        # ÉXITO: La eliminación fue exitosa o el tag no existía (retornó True)
        flash("Tag eliminado exitosamente.", "success")
        
    except TagVinculadoError as e:
        # FALLO (Vinculado): Se atrapa la excepción y se lee el atributo
        sitios_nombres = ", ".join(e.sitios_vinculados)
        flash(f"ERROR: El Tag no puede ser eliminado. Está asociado a los siguientes Sitios Históricos: {sitios_nombres}.", "error")

    except Exception:
        # FALLO (Otro Error): Error de DB, error inesperado, etc.
        flash("Ocurrió un error inesperado al intentar eliminar el Tag.", "error")
        
    return redirect(url_for("tags.index"))