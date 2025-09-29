from src.core import board
from src.core.database import db
from src.core.board.ciudad import Ciudad
from src.core.board.categoria_sitio import CategoriaSitio
from src.core.board.rol import Rol
from src.core.board.usuario import Usuario


def _get_ciudad_id(nombre_ciudad: str) -> int | None:
    c = db.session.query(Ciudad).filter(Ciudad.nombre == nombre_ciudad).first()
    return c.id if c else None


def _get_categoria_id(nombre_categoria: str) -> int | None:
    c = (
        db.session.query(CategoriaSitio)
        .filter(CategoriaSitio.nombre == nombre_categoria)
        .first()
    )
    return c.id if c else None


def run():
    # Crear rol y usuario "System" si no existen
    admin_role = db.session.query(Rol).filter(Rol.nombre == "Admin").first()
    if not admin_role:
        admin_role = Rol(nombre="Admin")
        db.session.add(admin_role)
        db.session.flush()

    system_user = db.session.query(Usuario).filter(Usuario.email == "system@example.com").first()
    if not system_user:
        system_user = Usuario(
            nombre="System",
            apellido="User",
            password="changeme",
            email="system@example.com",
            activo=True,
            esAdmin=True,
            idRol=admin_role.id,
        )
        db.session.add(system_user)
        db.session.flush()

    db.session.commit()

    # Crear sitios con el esquema actual utilizando board.crear_sitio
    # Asegúrate de haber corrido reset-db para tener ciudades y categorías seed-eadas
    data = [
        {
            "nombre": "Sitio Histórico 1",
            "descripcion": "Descripción breve del sitio histórico 1",
            "descripcion_completa": "Descripción completa del sitio histórico 1",
            "ciudad_nombre": "La Plata",
            "categoria_nombre": "Monumento",
            "latitud": -34.921,
            "longitud": -57.954,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "1850-01-01",
            "fecha_registro": "2022-01-15",
            "visible": "True",
            "baja": "False",      
        },
        {
            "nombre": "Sitio Histórico 2",
            "descripcion": "Descripción breve del sitio histórico 2",
            "descripcion_completa": "Descripción completa del sitio histórico 2",
            "ciudad_nombre": "Rosario",
            "categoria_nombre": "Edificio Histórico",
            "latitud": -32.944,
            "longitud": -60.650,
            "estado_conservacion": "Regular",
            "fecha_inauguracion": "1900-01-01",
            "fecha_registro": "2023-03-22",
            "visible": "True",
            "baja": "False",
        },
        {
            "nombre": "Sitio Histórico 3",
            "descripcion": "Descripción breve del sitio histórico 3",
            "descripcion_completa": "Descripción completa del sitio histórico 3",
            "ciudad_nombre": "Mendoza",
            "categoria_nombre": "Plaza",
            "latitud": -32.889,
            "longitud": -68.845,
            "estado_conservacion": "Malo",
            "fecha_inauguracion": "1750-01-01",
            "fecha_registro": "2021-11-05",
            "visible": "True",
            "baja": "False",
        },
    ]

    created = []
    for item in data:
        ciudad_id = _get_ciudad_id(item["ciudad_nombre"]) or None
        categoria_id = _get_categoria_id(item["categoria_nombre"]) or None
        form_like = {
            "nombre": item["nombre"],
            "descripcion": item["descripcion"],
            "descripcion_completa": item["descripcion_completa"],
            "ciudad": str(ciudad_id) if ciudad_id else "",
            "categoria": str(categoria_id) if categoria_id else "",
            "latitud": item["latitud"],
            "longitud": item["longitud"],
            "estado_conservacion": item["estado_conservacion"],
            "fecha_inauguracion": item["fecha_inauguracion"],
            "fecha_registro": item["fecha_registro"],
            "visible": item["visible"],
            "baja": item["baja"],
        }
        created.append(board.crear_sitio(form_like, id_usuario=system_user.id))

    print("Seeded sitios:")
    for s in created:
        print(" ", s)
