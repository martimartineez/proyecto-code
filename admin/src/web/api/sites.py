from flask import Blueprint, request, jsonify
from src.core.database import db
from src.core.entity.sitio_historico import SitioHistorico
from src.core.entity.ciudad import Ciudad
from src.core.entity.provincia import Provincia
from src.core.entity.tag import Tag
from src.web.controllers.sitios_historicos import filtrar
from sqlalchemy import func
from flask import Response
import json

bp = Blueprint('site_api', __name__, url_prefix='/api')

@bp.errorhandler(Exception)
def handle_api_errors(error):
    return jsonify({
        "error": {
            "code": "server_error",
            "message": "An unexpected error occurred"
        }
    }), 500

@bp.route('/sites', methods=['GET'])
def listar_sitios():
    name = request.args.get('name', '').strip()
    description = request.args.get('description', '').strip()
    city = request.args.get('city', '').strip()
    province = request.args.get('province', '').strip()
    tags = request.args.getlist('tags')
    order_by = request.args.get('order_by', 'name')
    lat = request.args.get('lat', type=float)
    long = request.args.get('long', type=float)
    radius = request.args.get('radius', type=float)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if (lat is not None and not (-90 <= lat <= 90)) or (long is not None and not (-180 <= long <= 180)) or (radius is not None and radius <= 0) or (page < 1) or (per_page < 1):
        return {
  "error": {
    "code": "invalid_query",
    "message": "Parameter validation failed",
    "details": {
      "lat": [
        "Must be a valid latitude"
      ],
      "long": [
        "Must be a valid longitude"
      ],
      "per_page": [
        "Must be between 1 and 100"
      ]
    }
  }
}, 400


    query = db.session.query(SitioHistorico).join(Ciudad).join(Provincia)
    if name:
        query = query.filter(SitioHistorico.nombre.ilike(f'%{name}%'))
    if description:
        query = query.filter(SitioHistorico.descBreve.ilike(f'%{description}%'))
    if city:
        query = query.filter(Ciudad.nombre.ilike(f'%{city}%'))
    if province:
        query = query.filter(Provincia.nombre.ilike(f'%{province}%'))
    if tags:
        if len(tags) == 1 and "," in tags[0]:
            tags = [t.strip() for t in tags[0].split(",") if t.strip()]
        query = query.join(SitioHistorico.tags).filter(Tag.nombre.in_(tags))
        query = query.group_by(SitioHistorico.id)
        query = query.having(func.count(func.distinct(Tag.id)) == len(tags))
    if lat is not None and long is not None and radius is not None:
        earth_radius = 6371 
        distance = earth_radius * func.acos(
            func.cos(func.radians(lat)) *
            func.cos(func.radians(SitioHistorico.latitud)) *
            func.cos(func.radians(SitioHistorico.longitud) - func.radians(long)) +
            func.sin(func.radians(lat)) *
            func.sin(func.radians(SitioHistorico.latitud))
        )

        query = query.filter(distance <= radius)


    total = query.count()
    offset = (page - 1) * per_page
    sitios = query.offset(offset).limit(per_page).all()


    return Response(
    json.dumps({
        "data": [s.to_dict() for s in sitios],
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": total
        }
    }, ensure_ascii=False),
    status=200,
    mimetype="application/json"
)


