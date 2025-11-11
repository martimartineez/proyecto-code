from __future__ import annotations
from flask import request, jsonify
from sqlalchemy import func, or_, and_
from sqlalchemy.exc import SQLAlchemyError
from src.web.api import bp
from src.core.database import db
from src.core.entity.sitio_historico import SitioHistorico
from src.core.entity.ciudad import Ciudad
from src.core.entity.provincia import Provincia
from src.core.entity.tag import Tag
import traceback


def _serialize_site(site: SitioHistorico) -> dict:
    ciudad_nombre = site.ciudad.nombre if site.ciudad else None
    provincia_nombre = (
        site.ciudad.provincia.nombre if site.ciudad and site.ciudad.provincia else None
    )
    return {
        "id": site.id,
        "nombre": site.nombre,
        "descripcion": site.descBreve,
        "ciudad": ciudad_nombre,
        "provincia": provincia_nombre,
        "estado": site.estadoConservacion,
        "fecha_registro": site.fechaRegistro.isoformat() if site.fechaRegistro else None,
        "lat": site.latitud,
        "lng": site.longitud,
        # Mostrar hasta 5 tags
        "tags": [t.nombre for t in (site.tags or [])][:5],
        # Campo para imagen de portada: no está en el modelo actual
        "cover_image": None,
    }


@bp.get("/sites")
def listar_sitios_publicos():
    """
    Lista sitios históricos públicos con búsqueda y filtros.

    Query params admitidos:
    - q: texto libre sobre nombre y descBreve
    - name, description: alias opcionales para compatibilidad
    - city: id de ciudad (int) o nombre (str)
    - province: id de provincia (int)
    - tags: múltiple (tags=1&tags=2) o csv (tags=1,2)
    - state: estado de conservación (ilike)
    - order_by: fecha_registro | nombre (default: fecha_registro)
    - order: asc | desc (default: desc)
    - page: int (default: 1)
    - per_page: int (default: 12)
    - lat, long, radius: filtro por radio en km (opcional)
    """
    try:
        q = (request.args.get("q") or "").strip()
        name = (request.args.get("name") or "").strip()
        description = (request.args.get("description") or "").strip()
        city_param = request.args.get("city")
        province_id = request.args.get("province", type=int)
        state = request.args.get("state")
        order_by = request.args.get("order_by", "fecha_registro")
        order = request.args.get("order", "desc")
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=12, type=int)
        lat = request.args.get("lat", type=float)
        lng = request.args.get("long", type=float)
        radius_km = request.args.get("radius", type=float)

        # Tags puede venir como repetido o CSV
        tags_values = request.args.getlist("tags")
        if len(tags_values) == 1 and "," in tags_values[0]:
            tags_values = [v for v in tags_values[0].split(",") if v]
        tag_ids = []
        for v in tags_values:
            try:
                tag_ids.append(int(v))
            except Exception:
                # ignorar no enteros
                continue

        query = db.session.query(SitioHistorico)

        # Solo visibles y no dados de baja
        query = query.filter(and_(SitioHistorico.visible.is_(True), SitioHistorico.baja.is_(False)))

        # Búsquedas por texto
        text_terms = [t for t in [q, name, description] if t]
        if text_terms:
            conditions = []
            for term in text_terms:
                ilike = f"%{term}%"
                conditions.append(SitioHistorico.nombre.ilike(ilike))
                conditions.append(SitioHistorico.descBreve.ilike(ilike))
            query = query.filter(or_(*conditions))

        # Filtros que requieren joins
        needs_ciudad_join = False
        needs_provincia_join = False

        if province_id:
            needs_provincia_join = True
            needs_ciudad_join = True

        if city_param:
            needs_ciudad_join = True

        if needs_provincia_join:
            query = query.join(Ciudad, SitioHistorico.idCiudad == Ciudad.id, isouter=True)
            query = query.join(Provincia, Ciudad.idProvincia == Provincia.id, isouter=True)
            if province_id:
                query = query.filter(Provincia.id == province_id)
        elif needs_ciudad_join:
            query = query.join(Ciudad, SitioHistorico.idCiudad == Ciudad.id, isouter=True)

        if city_param:
            try:
                city_id = int(city_param)
                query = query.filter(SitioHistorico.idCiudad == city_id)
            except Exception:
                # Buscar por nombre de ciudad (ilike) - requiere join
                if not needs_ciudad_join:
                    query = query.join(Ciudad, SitioHistorico.idCiudad == Ciudad.id, isouter=True)
                query = query.filter(Ciudad.nombre.ilike(f"%{city_param}%"))

        if state:
            query = query.filter(SitioHistorico.estadoConservacion.ilike(f"%{state}%"))

        if tag_ids:
            query = query.join(SitioHistorico.tags).filter(Tag.id.in_(tag_ids)).group_by(SitioHistorico.id).having(func.count(Tag.id) == len(tag_ids))

        # Filtro geográfico simple: bounding box aproximado por radio en km
        if lat is not None and lng is not None and radius_km is not None and radius_km > 0:
            # 1 grado lat ~ 111 km, 1 grado lon ~ 111*cos(lat)
            lat_delta = radius_km / 111.0
            lon_delta = radius_km / func.greatest(0.0001, 111.0 * func.cos(func.radians(lat)))
            query = query.filter(
                and_(
                    SitioHistorico.latitud.isnot(None),
                    SitioHistorico.longitud.isnot(None),
                    SitioHistorico.latitud.between(lat - lat_delta, lat + lat_delta),
                    SitioHistorico.longitud.between(lng - lon_delta, lng + lon_delta),
                )
            )

        # Orden
        order_map = {
            "fecha_registro": SitioHistorico.fechaRegistro,
            "nombre": SitioHistorico.nombre,
        }
        order_col = order_map.get(order_by, SitioHistorico.fechaRegistro)
        query = query.order_by(order_col.desc() if order.lower() == "desc" else order_col.asc())

        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()

        return jsonify(
            {
                "items": [_serialize_site(s) for s in items],
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page,
                "order_by": order_by,
                "order": order,
            }
        )
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "message": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Internal error", "message": str(e)}), 500


@bp.get("/filters/provinces")
def listar_provincias():
    provincias = db.session.query(Provincia).order_by(Provincia.nombre.asc()).all()
    return jsonify([{"id": p.id, "nombre": p.nombre} for p in provincias])


@bp.get("/filters/cities")
def listar_ciudades():
    province_id = request.args.get("province", type=int)
    q = (request.args.get("q") or "").strip()
    query = db.session.query(Ciudad)
    if province_id:
        query = query.filter(Ciudad.idProvincia == province_id)
    if q:
        query = query.filter(Ciudad.nombre.ilike(f"%{q}%"))
    cities = query.order_by(Ciudad.nombre.asc()).all()
    return jsonify([{"id": c.id, "nombre": c.nombre, "provincia_id": c.idProvincia} for c in cities])


@bp.get("/filters/tags")
def listar_tags():
    tags = db.session.query(Tag).filter(Tag.baja.is_(False)).order_by(Tag.nombre.asc()).all()
    return jsonify([{"id": t.id, "nombre": t.nombre, "slug": t.slug} for t in tags])

