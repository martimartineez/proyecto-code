from __future__ import annotations
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.web.handlers.auth import login_required
from src.core.board import feature_flags as ff_service
from src.core import auth as core_auth

NOMBRE_A_ETIQUETA = {
    "admin_maintenance_mode": "Mantenimiento del sistema de administración",
    "portal_maintenance_mode": "Mantenimiento del portal",
    "reviews_enabled": "Reseñas habilitadas",
}

bp = Blueprint("feature_flags", __name__, url_prefix="/feature_flags")

@bp.get("/")
@login_required
def index():
    flags = ff_service.list_flags()
    # Enrich flags with modifier user email if available
    enriched = []
    for f in flags:
        user_email = None
        if getattr(f, 'idUsuarioModificacion', None):
            u = core_auth.get_user_by_id(f.idUsuarioModificacion)
            user_email = u.email if u else None
        enriched.append({
            'nombre': f.nombre,
            'etiqueta': NOMBRE_A_ETIQUETA.get(f.nombre, f.nombre),
            'descripcion': f.descripcion,
            'valor': f.valor,
            'mensaje': f.mensaje,
            'ultimaModificacion': f.ultimaModificacion,
            'idUsuarioModificacion': f.idUsuarioModificacion,
            'usuarioEmail': user_email,
        })
    return render_template("feature_flags/index.html", flags=enriched)


@bp.post("/update")
@login_required
def update():
    nombre = request.form.get("nombre")
    if not nombre:
        flash("Flag inválido", "error")
        return redirect(url_for("feature_flags.index"))

    # Parse desired state and message
    new_valor = request.form.get("valor") == "on"
    mensaje = request.form.get("mensaje") or None

    # Validations
    max_len = 200
    if mensaje and len(mensaje) > max_len:
        flash(f"El mensaje no puede superar {max_len} caracteres", "error")
        return redirect(url_for("feature_flags.index"))

    # Require message when enabling maintenance modes
    if nombre in ("admin_maintenance_mode", "portal_maintenance_mode") and new_valor and not mensaje:
        flash("Debe especificar un mensaje de mantenimiento al habilitar este modo.", "error")
        return redirect(url_for("feature_flags.index"))

    uid = session.get('user_id')
    ff_service.update_flag(nombre, valor=new_valor, mensaje=mensaje, user_id=uid)

    estado = "ON" if new_valor else "OFF"
    flash(f"Flag '{nombre}' actualizado a {estado}", "success")
    return redirect(url_for("feature_flags.index"))
