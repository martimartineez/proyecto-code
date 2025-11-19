from flask import Blueprint, request, jsonify
from src.core.database import db
from src.core.entity.sitio_historico import SitioHistorico
from src.core.entity.ciudad import Ciudad
from src.core.auth import Usuario
from src.core.entity.provincia import Provincia
from src.core.entity.reseña import Reseña
from src.core.entity.tag import Tag
from sqlalchemy.orm import joinedload
from src.web.controllers.sitios_historicos import filtrar
from src.core.auth import devolver_usuario_publico_por_email

from sqlalchemy import func, or_
from flask import Response
import json
from src.core.auth.usuario import favoritos_usuarios_sitios
from src.core.entity.services import (
    obtener_sitio,
    registrar_evento_historial,
    listar_imagenes_sitio
)
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    jwt_required,
    get_jwt_identity,
)
from src.core.bcrypt import bcrypt
from datetime import timedelta
from flask_jwt_extended.exceptions import (
    NoAuthorizationError,
    InvalidHeaderError,
    JWTExtendedException,
)

bp = Blueprint("site_api", __name__, url_prefix="/api")


# AGREGAR CAMPOS A RESEÑAS INSERTED_AT Y UPDATED_AT


@bp.errorhandler(Exception)
def handle_api_errors(error):
    print(error)
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


@bp.errorhandler(NoAuthorizationError)
@bp.errorhandler(InvalidHeaderError)
@bp.errorhandler(JWTExtendedException)
def handle_jwt_errors(e):
    print(e)
    return (
        jsonify(
            {"error": {"code": "unauthorized", "message": "Authentication required"}}
        ),
        401,
    )


@bp.route("/sites", methods=["GET"])
def listar_sitios():
    name = request.args.get("name", "").strip()
    description = request.args.get("description", "").strip()
    q = request.args.get("q", "").strip()
    city = request.args.get("city", "").strip()
    province = request.args.get("province", "").strip()
    tags = request.args.getlist("tags")
    order_by = request.args.get("order_by", "name")
    order = request.args.get("order", "asc")
    lat = request.args.get("lat", type=float)
    long = request.args.get("long", type=float)
    radius = request.args.get("radius", type=float)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 25, type=int)
    state = request.args.get("state", "")

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
    # Solo sitios visibles y no dados de baja
    query = query.filter(
        SitioHistorico.visible.is_(True),
        SitioHistorico.baja.is_(False),
    )
    # Texto libre: si viene 'q', buscar por nombre OR descripción breve
    if q:
        query = query.filter(
            or_(
                SitioHistorico.nombre.ilike(f"%{q}%"),
                SitioHistorico.descBreve.ilike(f"%{q}%"),
            )
        )
    else:
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
    if state:
        query = query.filter(SitioHistorico.estadoConservacion.ilike(f"%{state}%"))
    if order_by:
        if order_by == "nombre":
            if order == "asc":
                query = query.order_by(SitioHistorico.nombre)
            else:
                query = query.order_by(SitioHistorico.nombre.desc())
        elif order_by == "fechaRegistro":
            if order == "asc":
                query = query.order_by(SitioHistorico.fechaRegistro)
            else:
                query = query.order_by(SitioHistorico.fechaRegistro.desc())

    total = query.count()
    offset = (page - 1) * per_page
    sitios = query.offset(offset).limit(per_page).all()

    return (
        jsonify(
            {
                "data": [s.to_dict() for s in sitios],
                "meta": {"page": page, "per_page": per_page, "total": total},
            }
        ),
        200,
    )


@bp.route("/sites", methods=["POST"])
@jwt_required()
def crear_sitio():
    data = request.get_json()
    if not data:
        return (
            jsonify(
                {
                    "erroraa": {
                        "code": "invalid_data",
                        "message": "Invalid input data",
                        "details": {" name": ["This field is required"]},
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
                    "errorcccc": {
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
    mail = get_jwt_identity()
    user = devolver_usuario_publico_por_email(mail)
    
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


@bp.route("/sites/<int:id>/is_favorite", methods=["GET"])
@jwt_required()
def check_favorite_status(id):
    sitio = obtener_sitio(id)
    if not sitio:
        return (
            jsonify({"error": {"code": "not_found", "message": "Site not found"}}),
            404,
        )

    # El usuario está logueado (garantizado por @jwt_required)
    user_email = get_jwt_identity() 
    user = db.session.query(Usuario).filter_by(email=user_email).first()
    
    is_favorite = False
    
    if user:
        # Consulta directa a la tabla de asociación para verificar el estado
        is_favorite_record = db.session.query(favoritos_usuarios_sitios).filter_by(
            usuarioId=user.id,
            sitioId=sitio.id
        ).first()
        
        if is_favorite_record:
            is_favorite = True
            
    # Devolver un JSON simple con el estado
    return jsonify({"is_favorite": is_favorite}), 200

@bp.route("/sites/<int:id>", methods=["GET"])
def obtener_sitio_api(id):
    sitio = obtener_sitio(id)
    if not sitio:
        return (
            jsonify({"error": {"code": "not_found", "message": "Site not found"}}),
            404,
        )
    
    # calcular promedio y conteo de reseñas aprobadas
    query_stats = db.session.query(
        func.avg(Reseña.puntaje).label('rating_avg'),
        func.count(Reseña.id).label('reviews_count')
    ).filter(Reseña.id_sitio == id, Reseña.estado == 'aprobada').first() # Solo reseñas aprobadas

    imagenes = listar_imagenes_sitio(id)



    data = sitio.to_dict()
    
    # añadir las estadísticas al diccionario

    data['rating_avg'] = round(query_stats.rating_avg, 1) if query_stats.rating_avg else 'N/A'
    data['reviews_count'] = query_stats.reviews_count if query_stats.reviews_count else 0

    # añadir las imágenes al diccionario
    data['images'] = [
        {
            "url": img.url_publica,
            "alt": img.titulo_alt,
            "portada": img.portada
        } for img in imagenes
    ]

    return jsonify(data), 200


@bp.route("/auth", methods=["POST"])
def auth():

    data = request.get_json()
    email = data.get("user")
    password = data.get("password")
    user = db.session.query(Usuario).filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(
            identity=str(user.email), expires_delta=timedelta(hours=1)
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


@bp.route("/sites/<int:id>/reviews", methods=["GET"])
# @jwt_required()
def listar_resenas_sitio(id):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    order_by = request.args.get("order_by", "inserted_at") # Valor por defecto: fecha
    order = request.args.get("order", "desc")              # Valor por defecto: descendente

    sitio = obtener_sitio(id)

    if not sitio:
        return (
            jsonify({"error": {"code": "not_found", "message": "Site not found"}}),
            404,
        )

    if page < 1 or per_page < 1 or per_page > 100:
        return (
            jsonify(
                {
                    "error": {
                        "code": "invalid_data",
                        "message": "Invalid input data",
                        "details": {"per_page": ["Must be between 1 and 100"]},
                    }
                }
            ),
            400,
        )

    query = db.session.query(Reseña).filter_by(id_sitio=id, estado='aprobada')

    query = query.options(joinedload(Reseña.usuario))

    sort_column = Reseña.inserted_at 
    if order_by == "rating":
        sort_column = Reseña.puntaje
    
    if order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    total = query.count()
    offset = (page - 1) * per_page

    resenas = query.offset(offset).limit(per_page).all()
    data = [
        {
            "id": r.id,
            "site_id": r.id_sitio,
            "rating": r.puntaje,
            "comment": r.texto,
            "user_alias": r.usuario.nombre if r.usuario else "Usuario Anónimo",
            "inserted_at": r.inserted_at.isoformat() + "Z" if r.inserted_at else None,
            "updated_at": r.updated_at.isoformat() + "Z" if r.updated_at else None,
        }
        for r in resenas
    ]
    return (
        jsonify(
            {"data": data, "meta": {"page": page, "per_page": per_page, "total": total}}
        ),
        200,
    )


@bp.route("/sites/<int:id_sitio>/reviews", methods=["POST"])
@jwt_required()
def crear_resena_sitio(id_sitio):
    data = request.get_json()
    texto = data.get("comment")
    puntaje = data.get("rating")

    sitio = obtener_sitio(id_sitio)
    if not sitio or not texto or puntaje is None:
        return (
            jsonify({"error": {"code": "not_found", "message": "Site not found"}}),
            404,
        )

    if not texto or puntaje is None or float(puntaje) < 1 or float(puntaje) > 5 or len(texto) < 20:
        return (
            jsonify(
                {
                    "error": {
                        "code": "invalid_data",
                        "message": "Invalid input data",
                        "details": {"rating": ["Must be between 1 and 5"]},
                    }
                }
            ),
            400,
        )

    email = get_jwt_identity()
    user = devolver_usuario_publico_por_email(email).id
    nueva_resena = Reseña(
        texto=texto, puntaje=puntaje, id_usuario=user, id_sitio=id_sitio
    )
    db.session.add(nueva_resena)
    db.session.commit()
    return (
        jsonify(
            {
                "id": nueva_resena.id,
                "texto": nueva_resena.texto,
                "puntaje": nueva_resena.puntaje,
                "usuario_id": nueva_resena.id_usuario,
                "sitio_id": nueva_resena.id_sitio,
                "inserted_at": nueva_resena.inserted_at.isoformat(),
                "updated_at": nueva_resena.updated_at.isoformat(),
            }
        ),
        201,
    )


@bp.route("/sites/<int:id_sitio>/reviews/<int:id_resena>", methods=["GET"])
@jwt_required()
def obtener_resena_por_idSitio(id_sitio, id_resena):
    if id_resena < 1:
        return (
            jsonify(
                {
                    "error": {
                        "code": "invalid_data",
                        "message": "Invalid input data",
                        "details": {"review_id": ["Must be a positive integer"]},
                    }
                }
            ),
            400,
        )

    sitio = obtener_sitio(id_sitio)

    if not sitio:
        return (
            jsonify({"error": {"code": "not_found", "message": "Site not found"}}),
            404,
        )
    resena = db.session.query(Reseña).filter_by(id=id_resena, id_sitio=id_sitio).first()
    if not resena:
        return (
            jsonify({"error": {"code": "not_found", "message": "Review not found"}}),
            404,
        )

    data = {
        "id": resena.id,
        "site_id": resena.id_sitio,
        "rating": resena.puntaje,
        "comment": resena.texto,
        "inserted_at": resena.inserted_at.isoformat() + "Z" if resena.inserted_at else None,
        "updated_at": resena.updated_at.isoformat() + "Z" if resena.updated_at else None,
    }

    return jsonify(data), 200


@bp.route("/sites/<int:id_sitio>/reviews/<int:id_resena>", methods=["DELETE"])
@jwt_required()
def eliminar_reseña_poridSitio(id_sitio, id_resena):
    sitio = obtener_sitio(id_sitio)
    resena = db.session.query(Reseña).filter_by(id=id_resena, id_sitio=id_sitio).first()

    if not sitio or not resena:
        return (
            jsonify({"error": {"code": "not_found", "message": "Review not found"}}),
            404,
        )

    email = get_jwt_identity()
    user = devolver_usuario_publico_por_email(email)
    user_id = user.id
    if resena.id_usuario != user_id:
        return (
            jsonify(
                {
                    "error": {
                        "code": "forbidden",
                        "message": "You do not have permission to delete this review",
                    }
                }
            ),
            403,
        )

    db.session.delete(resena)
    db.session.commit()

    return "", 204


@bp.route("/sites/<int:id_sitio>/favorite", methods=["PUT"])
@jwt_required()
def marcar_sitio_como_favorito(id_sitio):
    sitio = obtener_sitio(id_sitio)
    if not sitio:
        return (
            jsonify({"error": {"code": "not_found", "message": "Site not found"}}),
            404,
        )

    email = get_jwt_identity()
    user = devolver_usuario_publico_por_email(email)
    if sitio in user.favoritos:
        return "", 204
    user.favoritos.append(sitio)
    db.session.commit()
    return "", 204


@bp.route("/sites/<int:id_sitio>/favorite", methods=["DELETE"])
@jwt_required()
def desmarcar_sitio_como_favorito(id_sitio):
    sitio = obtener_sitio(id_sitio)
    if not sitio:
        return (
            jsonify({"error": {"code": "not_found", "message": "Site not found"}}),
            404,
        )

    email = get_jwt_identity()
    user = devolver_usuario_publico_por_email(email)
    if sitio not in user.favoritos:
        return "", 204
    user.favoritos.remove(sitio)
    db.session.commit()
    return "", 204


@bp.route("/me/favorites", methods=["GET"])
@jwt_required()
def mostrar_todos_favoritos():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    if page < 1 or per_page < 1 or per_page > 100:
        return (
            jsonify(
                {
                    "error": {
                        "code": "invalid_data",
                        "message": "Invalid input data",
                        "details": {"per_page": ["Must be between 1 and 100"]},
                    }
                }
            ),
            400,
        )

    email = get_jwt_identity()
    user = devolver_usuario_publico_por_email(email)
    user_id = user.id
    query = (
        db.session.query(SitioHistorico)
        .join(favoritos_usuarios_sitios)
        .filter(favoritos_usuarios_sitios.c.usuario_id == user_id)
    )

    total = query.count()
    offset = (page - 1) * per_page
    sitios = query.offset(offset).limit(per_page).all()

    data = [s.to_dict() for s in sitios]

    return (
        jsonify(
            {"data": data, "meta": {"page": page, "per_page": per_page, "total": total}}
        ),
        200,
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

@bp.route('/google', methods=['POST', 'OPTIONS'])
def login_google():

    from flask import Blueprint, request, jsonify
    from google.oauth2 import id_token
    from google.auth.transport import requests
    from flask_jwt_extended import create_access_token, set_access_cookies
    from src.core.auth import checkear_usuario_publico_existente, create_user, actualizar_usuario_publico

    # Preflight CORS
    if request.method == "OPTIONS":
        return {}, 200

    data = request.get_json()
    token = data.get("token")

    if not token:
        return jsonify({"success": False, "error": "No token provided"}), 400

    try:
        # Verificar token de Google
        info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            "501426149813-3ldbtlaur9oodqe8eq5rhuqrecjn22s7.apps.googleusercontent.com"
        )
        print(info)

        # Crear o actualizar usuario en la base de datos
        if (checkear_usuario_publico_existente(info["email"]) == False):
            create_user(
                nombre=info.get("given_name"),
                email=info.get("email"),
                apellido=info.get("family_name"),
                activo=True,
                esAdmin=False,
                foto=info.get("picture"),
                publico = True
            )
        else:
            actualizar_usuario_publico(info["email"], info)
            
        
        # Crear token propio (sesión)
        access_token = create_access_token(identity=info["email"])
        # Respuesta con cookie
        resp = jsonify({
            "success": True,
            }
        )

        # 👉 Guarda la cookie en el navegador automáticamente
        set_access_cookies(resp, access_token)
        
        return resp, 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
    

@bp.get('/perfil')
@jwt_required()
def perfil():

    from src.core.auth import devolver_usuario_publico_por_email

    email = get_jwt_identity()
    usuario = devolver_usuario_publico_por_email(email)
    return usuario.to_dict(), 200

@bp.route('/boton', methods=['GET'])
@jwt_required()
def boton():
    return jsonify({"message": "¡La ruta de prueba funciona correctamente!"}), 200

@bp.route("/logout", methods=["POST"])
def logout():
    from flask import jsonify
    from flask_jwt_extended import unset_jwt_cookies

    resp = jsonify({"msg": "logout exitoso"})
    unset_jwt_cookies(resp)  # 👈 esto borra las cookies access y refresh
    return resp, 200

@bp.route('/reseñas_usuario', methods=['GET'])
@jwt_required()
def reseñas_usuario():
    from src.core.entity.services import listar_reseñas_usuario
    from src.core.auth import devolver_usuario_publico_por_email


    user_email = get_jwt_identity()
    user = devolver_usuario_publico_por_email(user_email)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    reseñas = listar_reseñas_usuario(user.id)
    # Convertir a diccionarios
    reseñas_json = [
        {
            "sitio": r.sitio.nombre,
            "texto": r.texto,
            "puntuacion": r.puntaje,
            "fecha": r.inserted_at.isoformat() if r.inserted_at else None,
            # agregar lo que necesites
        }
        for r in reseñas
    ]

    #print("reseñas_json:", reseñas_json)  # Depuración

    return jsonify({"reseñas": reseñas_json}), 200


    