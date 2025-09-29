from src.core import board
from src.core.database import db
from src.core.board.ciudad import Ciudad
from src.core.board.categoria_sitio import CategoriaSitio


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
    # Crear sitios con el esquema actual utilizando board.crear_sitio
    # Asegúrate de haber corrido reset-db para tener ciudades y categorías seed-eadas
    data = [
        {
            "nombre": "Casa Rosada",
            "descripcion": "Sede del Poder Ejecutivo de la República Argentina",
            "descripcion_completa": "Edificio gubernamental histórico, sede de la Presidencia de la Nación Argentina. Su característico color rosa y su ubicación en Plaza de Mayo la convierten en un ícono nacional.",
            "ciudad_nombre": "La Plata",
            "categoria_nombre": "Edificio Histórico",
            "latitud": -34.6083,
            "longitud": -58.3712,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "1884-05-25",
            "fecha_registro": "2022-01-15",
        },
        {
            "nombre": "Teatro Colón",
            "descripcion": "Principal teatro de ópera de Argentina",
            "descripcion_completa": "Considerado uno de los mejores teatros líricos del mundo por su acústica y arquitectura. Sede de importantes presentaciones de ópera, ballet y música clásica.",
            "ciudad_nombre": "La Plata",
            "categoria_nombre": "Edificio Histórico",
            "latitud": -34.6010,
            "longitud": -58.3831,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "1908-05-25",
            "fecha_registro": "2022-02-20",
        },
        {
            "nombre": "Catedral de La Plata",
            "descripcion": "Mayor templo neogótico de América del Sur",
            "descripcion_completa": "Imponente catedral neogótica, una de las más grandes de América Latina. Sus torres alcanzan los 112 metros de altura y su construcción llevó casi 100 años.",
            "ciudad_nombre": "La Plata",
            "categoria_nombre": "Monumento",
            "latitud": -34.9205,
            "longitud": -57.9537,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "1932-11-19",
            "fecha_registro": "2022-03-10",
        },
        {
            "nombre": "Monumento Nacional a la Bandera",
            "descripcion": "Monumento histórico dedicado a la bandera argentina",
            "descripcion_completa": "Complejo monumental que homenajea a la bandera nacional y a su creador Manuel Belgrano. Incluye una torre mirador y una llama votiva eterna.",
            "ciudad_nombre": "Rosario",
            "categoria_nombre": "Monumento",
            "latitud": -32.9444,
            "longitud": -60.6306,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "1957-06-20",
            "fecha_registro": "2022-06-15",
        },
        {
            "nombre": "Plaza San Martín",
            "descripcion": "Plaza histórica en el centro de Mendoza",
            "descripcion_completa": "Plaza principal de la ciudad, nombrada en honor al General José de San Martín. Punto de encuentro histórico y centro cívico de la ciudad.",
            "ciudad_nombre": "Mendoza",
            "categoria_nombre": "Plaza",
            "latitud": -32.8908,
            "longitud": -68.8272,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "1813-01-01",
            "fecha_registro": "2022-07-20",
        },
        {
            "nombre": "Basílica de San Francisco",
            "descripcion": "Templo histórico del siglo XIX",
            "descripcion_completa": "Iglesia de estilo neoclásico italiano, sobreviviente del terremoto de 1861. Importante centro religioso y cultural de la ciudad.",
            "ciudad_nombre": "Mendoza",
            "categoria_nombre": "Edificio Histórico",
            "latitud": -32.8892,
            "longitud": -68.8275,
            "estado_conservacion": "Regular",
            "fecha_inauguracion": "1875-10-15",
            "fecha_registro": "2022-08-05",
        },
        {
            "nombre": "Palacio Municipal de Rosario",
            "descripcion": "Sede del gobierno municipal de Rosario",
            "descripcion_completa": "Edificio de estilo ecléctico francés, sede del poder ejecutivo municipal. Su arquitectura refleja la prosperidad de principios del siglo XX.",
            "ciudad_nombre": "Rosario",
            "categoria_nombre": "Edificio Histórico",
            "latitud": -32.9442,
            "longitud": -60.6332,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "1896-07-01",
            "fecha_registro": "2022-09-12",
        },
        {
            "nombre": "Plaza Independencia",
            "descripcion": "Plaza principal de Mendoza",
            "descripcion_completa": "Principal espacio verde de la ciudad, diseñada después del terremoto de 1861. Centro neurálgico de actividades culturales y recreativas.",
            "ciudad_nombre": "Mendoza",
            "categoria_nombre": "Plaza",
            "latitud": -32.8894,
            "longitud": -68.8457,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "1861-12-01",
            "fecha_registro": "2022-10-20",
        },
        {
            "nombre": "Museo de La Plata",
            "descripcion": "Principal museo de ciencias naturales del país",
            "descripcion_completa": "Museo de historia natural y antropología más importante de Sudamérica. Su colección incluye fósiles, minerales y piezas arqueológicas.",
            "ciudad_nombre": "La Plata",
            "categoria_nombre": "Edificio Histórico",
            "latitud": -34.9052,
            "longitud": -57.9493,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "1888-11-19",
            "fecha_registro": "2022-11-15",
        },
        {
            "nombre": "Antiguo Mercado Central",
            "descripcion": "Ex mercado convertido en centro cultural",
            "descripcion_completa": "Edificio histórico que funcionó como mercado central y ahora es un importante centro cultural. Conserva su arquitectura original del siglo XIX.",
            "ciudad_nombre": "Rosario",
            "categoria_nombre": "Edificio Histórico",
            "latitud": -32.9465,
            "longitud": -60.6393,
            "estado_conservacion": "Regular",
            "fecha_inauguracion": "1889-05-01",
            "fecha_registro": "2022-12-01",
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
        }
        created.append(board.crear_sitio(form_like))

    print("Seeded sitios:")
    for s in created:
        print(" ", s)
