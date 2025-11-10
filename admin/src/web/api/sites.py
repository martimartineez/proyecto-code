from flask import Blueprint, request, jsonify
from src.core.database import db
from src.core.entity.sitio_historico import SitioHistorico
from src.core.entity.ciudad import Ciudad
from src.core.auth import Usuario
from src.core.entity.provincia import Provincia
from src.core.entity.tag import Tag
from src.web.controllers.sitios_historicos import filtrar
from sqlalchemy import func
from flask import Response
import json
from src.core.entity.services import (
    obtener_sitio,
    registrar_evento_historial,
    obtener_sitio,
)
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    jwt_required,
    get_jwt_identity,
)
from src.core.bcrypt import bcrypt
from datetime import timedelta

bp = Blueprint("site_api", __name__, url_prefix="/api")


@bp.errorhandler(Exception)
def handle_api_errors(error):
    return (
        jsonify(
            {
                "error": {
                    "code": "server_error",
                    "message": "An unexpected error occurred",
                }
            }
        ),
        500,
    )


@bp.route("/sites", methods=["GET"])
def listar_sitios():
    name = request.args.get("name", "").strip()
    description = request.args.get("description", "").strip()
    city = request.args.get("city", "").strip()
    province = request.args.get("province", "").strip()
    tags = request.args.getlist("tags")
    order_by = request.args.get("order_by", "name")
    lat = request.args.get("lat", type=float)
    long = request.args.get("long", type=float)
    radius = request.args.get("radius", type=float)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    if (
        (lat is not None and not (-90 <= lat <= 90))
        or (long is not None and not (-180 <= long <= 180))
        or (radius is not None and radius <= 0)
        or (page < 1)
        or (per_page < 1)
    ):
        return {
            "error": {
                "code": "invalid_query",
                "message": "Parameter validation failed",
                "details": {
                    "lat": ["Must be a valid latitude"],
                    "long": ["Must be a valid longitude"],
                    "per_page": ["Must be between 1 and 100"],
                },
            }
        }, 400

    query = db.session.query(SitioHistorico).join(Ciudad).join(Provincia)
    if name:
        query = query.filter(SitioHistorico.nombre.ilike(f"%{name}%"))
    if description:
        query = query.filter(SitioHistorico.descBreve.ilike(f"%{description}%"))
    if city:
        query = query.filter(Ciudad.nombre.ilike(f"%{city}%"))
    if province:
        query = query.filter(Provincia.nombre.ilike(f"%{province}%"))
    if tags:
        if len(tags) == 1 and "," in tags[0]:
            tags = [t.strip() for t in tags[0].split(",") if t.strip()]
        query = query.join(SitioHistorico.tags).filter(Tag.nombre.in_(tags))
        query = query.group_by(SitioHistorico.id)
        query = query.having(func.count(func.distinct(Tag.id)) == len(tags))
    if lat is not None and long is not None and radius is not None:
        earth_radius = 6371
        distance = earth_radius * func.acos(
            func.cos(func.radians(lat))
            * func.cos(func.radians(SitioHistorico.latitud))
            * func.cos(func.radians(SitioHistorico.longitud) - func.radians(long))
            + func.sin(func.radians(lat))
            * func.sin(func.radians(SitioHistorico.latitud))
        )

        query = query.filter(distance <= radius)

    total = query.count()
    offset = (page - 1) * per_page
    sitios = query.offset(offset).limit(per_page).all()

    return Response(
        json.dumps(
            {
                "data": [s.to_dict() for s in sitios],
                "meta": {"page": page, "per_page": per_page, "total": total},
            },
            ensure_ascii=False,
        ),
        status=200,
        mimetype="application/json",
    )


@bp.route("/sites", methods=["POST"])
@jwt_required()
def crear_sitio():
    try:
        data = request.get_json()

        if not data:
            return (
                jsonify(
                    {
                        "error": {
                            "code": "invalid_data",
                            "message": "Invalid input data",
                            "details": {" name": ["This field is required"]},
                        }
                    }
                ),
                400,
            )

        existe = obtener_sitio(data.get("id"))
        if existe:
            return (
                jsonify(
                    {
                        "error": {
                            "code": "invalid_data",
                            "message": "Invalid input data",
                            "details": {"name": ["This field is required"]},
                        }
                    }
                ),
                400,
            )
        data = request.get_json()
        errores = validar_datos_sitio(data)
        if errores:
            return (
                jsonify(
                    {
                        "error": {
                            "code": "invalid_data",
                            "message": "Invalid input data",
                            "details": errores,
                        }
                    }
                ),
                400,
            )
        provincia = (
            db.session.query(Provincia).filter_by(nombre=data.get("province")).first()
        )
        ciudad = (
            db.session.query(Ciudad)
            .filter_by(nombre=data.get("city"), idProvincia=provincia.id)
            .first()
        )

        sitio = SitioHistorico(
            nombre=data["name"],
            descBreve=data.get("short_description"),
            descCompleta=data.get("description"),
            ciudad=ciudad,
            latitud=data["lat"],
            longitud=data["long"],
            estadoConservacion=data["state_of_conservation"],
            visible=True,
            baja=False,
        )
        db.session.add(sitio)

        for tag_nombre in data.get("tags", []):
            tag = db.session.query(Tag).filter_by(nombre=tag_nombre).first()
            if not tag:
                tag = Tag(nombre=tag_nombre, slug=tag_nombre.lower())
                db.session.add(tag)
                db.session.flush()
            sitio.tags.append(tag)

        db.session.commit()
        user_id = get_jwt_identity()
        user = db.session.query(Usuario).get(user_id)
        registrar_evento_historial(
            id_sitio=sitio.id,
            id_usuario=user.id,
            accion="CREATED",
            valores_anteriores=None,
            valores_nuevos={
                "nombre": sitio.nombre,
                "idCiudad": sitio.idCiudad,
                "idCategoria": sitio.idCategoria,
                "latitud": sitio.latitud,
                "longitud": sitio.longitud,
                "visible": sitio.visible,
                "baja": sitio.baja,
                "tags": [t.nombre for t in getattr(sitio, "tags", [])],
            },
        )

        return jsonify(sitio.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        print(e)
        jsonify(
            {
                {
                    "error": {
                        "code": "server_error",
                        "message": "An unexpected error occurred",
                    }
                }
            }
        )


@bp.route("/sites/<int:id>", methods=["GET"])
def obtener_sitio_api(id):
    try:
        sitio = obtener_sitio(id)
        if not sitio:
            return (
                jsonify({"error": {"code": "not_found", "message": "Site not found"}}),
                404,
            )
        return jsonify(sitio.to_dict()), 200
    except Exception as e:
        print(e)
        return (
            jsonify(
                {
                    "error": {
                        "code": "server_error",
                        "message": "An unexpected error occurred",
                    }
                }
            ),
            500,
        )


@bp.route("/auth", methods=["POST"])
def auth():
    try:
        data = request.get_json()
        email = data.get("user")
        password = data.get("password")
        user = db.session.query(Usuario).filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(
                identity=str(user.id), expires_delta=timedelta(hours=1)
            )
            expires = timedelta(hours=1)
            return (
                jsonify(
                    {"token": access_token, "expires_in": int(expires.total_seconds())}
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "error": {
                            "code": "invalid_credentials",
                            "message": "Credenciales inválidas.",
                        }
                    }
                ),
                401,
            )
    except Exception as e:
        print(e)
        return (
            jsonify(
                {
                    "error": {
                        "code": "server_error",
                        "message": "An unexpected error occurred",
                    }
                }
            ),
            500,
        )


def validar_datos_sitio(data):
    errores = {}

    required_fields = {
        "name": "Site name is required",
        "province": "Province is required",
        "city": "City is required",
        "lat": "Latitude is required",
        "long": "Longitude is required",
        "state_of_conservation": "State of conservation is required",
    }

    for field, msg in required_fields.items():
        if not data.get(field):
            errores[field] = [msg]

    return errores
