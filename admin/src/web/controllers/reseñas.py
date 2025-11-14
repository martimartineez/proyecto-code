from flask import Blueprint, render_template, request, url_for, redirect, flash
from src.core.database import db
from src.core.entity.reseña import Reseña
from src.core.auth.usuario import Usuario
from src.core.entity.sitio_historico import SitioHistorico
from src.core.entity.services.__init__ import listar_sitios
from datetime import date
from sqlalchemy import or_, asc, desc
from math import ceil

bp = Blueprint("reseñas", __name__, url_prefix="/reseñas")

@bp.route("/", methods=["GET"])
def listar_reseñas():
    estado = request.args.get("estado")
    sitio = request.args.get("sitio")
    puntaje = request.args.get("puntaje")
    fecha_desde = request.args.get("fecha_desde")
    fecha_hasta = request.args.get("fecha_hasta")
    buscar = request.args.get("buscar")

    sort_by = request.args.get("sort_by", "fecha") 
    order = request.args.get("order", "asc") 

    page = int(request.args.get("page", 1))
    per_page = 25


    query = db.session.query(Reseña)
    if estado:
        query = query.filter(Reseña.estado == estado)
    if sitio:
        query = query.filter(Reseña.id_sitio == sitio)
    if puntaje:
        query = query.filter(Reseña.puntaje == int(puntaje))
    if fecha_desde:
        query = query.filter(Reseña.inserted_at >= fecha_desde)
    if fecha_hasta:
        query = query.filter(Reseña.inserted_at <= fecha_hasta)
    if buscar:
        pattern = f"%{buscar}%"
        query = query.join(Usuario).filter(
        or_(
            Reseña.texto.ilike(pattern),
            Usuario.email.ilike(pattern)
        )
    )
        
    order_func = asc if order == "asc" else desc
    if sort_by == "puntaje":
        query = query.order_by(order_func(Reseña.puntaje))
    else:
        query = query.order_by(order_func(Reseña.inserted_at))


    total_results = query.count()
    total_pages = (total_results + per_page - 1) // per_page
    resenas = query.offset((page - 1) * per_page).limit(per_page).all()
    
    args = request.args.to_dict(flat=False)
    args.pop("page", None)
    sitios = listar_sitios()
    return render_template("reseñas/index.html",resenas=resenas, sitios=sitios,total_results=total_results,date=date,request_args=args,total_pages=total_pages,page=page)



@bp.route("/<int:resena_id>/aprobar", methods=["POST"])
def aprobar_reseña(resena_id):
    reseña = db.session.query(Reseña).get(resena_id)
    if reseña:
        reseña.estado = "aprobada"
        db.session.commit()
    
    flash("¡La reseña ha sido aprobada correctamente!", "success")
    return redirect(url_for("reseñas.listar_reseñas"))

@bp.route("/<int:resena_id>/eliminar", methods=["POST"])
def eliminar_reseña(resena_id):
    reseña = db.session.query(Reseña).get(resena_id)
    if reseña:
        db.session.delete(reseña)
        db.session.commit()

    flash("¡La reseña ha sido eliminada correctamente!", "success")
    
    return redirect(url_for("reseñas.listar_reseñas"))


@bp.route("/<int:resena_id>/rechazar", methods=["POST"])
def rechazar_reseña(resena_id):
    motivo = request.form.get("motivo")
    reseña = db.session.query(Reseña).get(resena_id)
    if reseña:
        reseña.estado = "rechazada"
        reseña.motivo = motivo
        db.session.commit()

    flash("¡La reseña ha sido rechazada correctamente!", "success")
    
    return redirect(url_for("reseñas.listar_reseñas"))

@bp.route("/reseña/<int:resena_id>", methods=["GET"])
def ver_detalles_reseña(resena_id):
    reseña = db.session.query(Reseña).get(resena_id)
    if not reseña:
        return "Reseña no encontrada", 404
    return render_template("reseñas/detalles.html", resena=reseña)