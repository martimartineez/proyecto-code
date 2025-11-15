from __future__ import annotations
from typing import List, Optional
from datetime import datetime, timezone

from src.core.database import db
from src.core.entity.feature_flag import FeatureFlag

DEFAULT_FLAGS = [
    {
        "nombre": "admin_maintenance_mode",
        "descripcion": "Bloquea rutas de administración (excepto login).",
        "valor": False,
        "mensaje": None,
    },
    {
        "nombre": "portal_maintenance_mode",
        "descripcion": "Pone el portal en modo mantenimiento.",
        "valor": False,
        "mensaje": None,
    },
    {
        "nombre": "reviews_enabled",
        "descripcion": "Habilita o deshabilita la creación de reseñas en el portal.",
        "valor": True,
        "mensaje": None,
    },
]


def ensure_default_flags() -> None:
    """Crea los feature flags por defecto si no existen."""
    existing = {ff.nombre for ff in db.session.query(FeatureFlag.nombre).all()}  # type: ignore[arg-type]
    created = False
    for data in DEFAULT_FLAGS:
        if data["nombre"] not in existing:
            db.session.add(FeatureFlag(**data))
            created = True
    if created:
        db.session.commit()


def list_flags() -> List[FeatureFlag]:
    return db.session.query(FeatureFlag).order_by(FeatureFlag.nombre.asc()).all()


def get_flag(nombre: str) -> Optional[FeatureFlag]:
    return db.session.query(FeatureFlag).filter(FeatureFlag.nombre == nombre).first()


def update_flag(nombre: str, *, valor: Optional[bool] = None, mensaje: Optional[str] = None, user_id: Optional[int] = None) -> FeatureFlag:
    flag = get_flag(nombre)
    if not flag:
        # autocreate if missing
        flag = FeatureFlag(nombre=nombre, descripcion=None, valor=False, mensaje=None)
        db.session.add(flag)
        db.session.flush()

    if valor is not None:
        flag.valor = valor
    if mensaje is not None:
        flag.mensaje = mensaje

    flag.ultimaModificacion = datetime.now(timezone.utc)
    flag.idUsuarioModificacion = user_id

    db.session.commit()
    return flag
