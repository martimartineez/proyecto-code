from src.core import board
from src.core.board import seeds as board_seeds
from src.core import auth
from src.core.database import db
from src.core.board.ciudad import Ciudad
from src.core.board.categoria_sitio import CategoriaSitio
from src.core.board.rol import Rol
from src.core.auth import Usuario
from src.core.board.sitio_historico import SitioHistorico


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
    # 0) Seed geografía completa (Provincias y Ciudades) y Categorías
    try:
        board_seeds.seed_geografia_completa()
    except Exception as exc:
        print(f"Error en seed_geografia_completa: {exc}")
    try:
        board_seeds.seed_categorias()
    except Exception as exc:
        print(f"Error en seed_categorias: {exc}")


    system_user = auth.create_user(
        nombre="System",
        apellido="User",
        password="changeme",
        email="system@example.com",
        activo=True,
        esAdmin=True,
    )

    db.session.commit()

    # Crear sitios con el esquema actual utilizando board.crear_sitio
    # Asegúrate de haber corrido reset-db para tener ciudades y categorías seed-eadas
    if db.session.query(SitioHistorico).count() > 0:
        return
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
        {
            "nombre": "Parque Independencia",
            "descripcion": "Principal parque urbano de Rosario",
            "descripcion_completa": "Gran espacio verde diseñado por el paisajista Carlos Thays. Alberga lagos, jardines, un zoológico y varios monumentos históricos.",
            "ciudad_nombre": "Rosario",
            "categoria_nombre": "Parque",
            "latitud": -32.9460,
            "longitud": -60.6390,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "1900-09-15",
            "fecha_registro": "2023-01-10",
        },
        {
            "nombre": "Cerro de la Gloria",
            "descripcion": "Monumento histórico en Mendoza",
            "descripcion_completa": "Monumento que conmemora la gesta libertadora del General San Martín. Ofrece vistas panorámicas de la ciudad y los Andes.",
            "ciudad_nombre": "Mendoza",
            "categoria_nombre": "Monumento",
            "latitud": -32.8905,
            "longitud": -68.8310,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "1914-02-12",
            "fecha_registro": "2023-02-18",
        },
        {
            "nombre": "Teatro Mendoza",
            "descripcion": "Principal teatro de la ciudad de Mendoza",
            "descripcion_completa": "Teatro histórico que ha sido escenario de importantes obras de teatro, ópera y conciertos. Su arquitectura refleja el estilo neoclásico.",
            "ciudad_nombre": "Mendoza",
            "categoria_nombre": "Edificio Histórico",
            "latitud": -32.8900,
            "longitud": -68.8270,
            "estado_conservacion": "Regular",
            "fecha_inauguracion": "1925-11-25",
            "fecha_registro": "2023-03-05",
        },
        {
            "nombre": "Parque España",
            "descripcion": "Parque urbano a orillas del río Paraná",
            "descripcion_completa": "Espacio verde con áreas recreativas, culturales y deportivas. Ofrece vistas panorámicas del río y es un punto de encuentro popular.",
            "ciudad_nombre": "Rosario",
            "categoria_nombre": "Parque",
            "latitud": -32.9468,
            "longitud": -60.6400,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "1992-03-03",
            "fecha_registro": "2023-04-12",
        },
        {
            "nombre": "Catedral Basílica de Nuestra Señora del Rosario",
            "descripcion": "Catedral principal de Rosario",
            "descripcion_completa": "Imponente catedral neogótica ubicada en el centro de la ciudad. Es un importante centro religioso y turístico.",
            "ciudad_nombre": "Rosario",
            "categoria_nombre": "Edificio Histórico",
            "latitud": -32.9463,
            "longitud": -60.6395,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "1887-11-07",
            "fecha_registro": "2023-05-20",
        },
        {
            "nombre": "Plaza 25 de Mayo",
            "descripcion": "Plaza histórica en el centro de La Plata",
            "descripcion_completa": "Plaza principal de la ciudad, diseñada por el arquitecto Pedro Benoit. Rodeada de edificios históricos y monumentos.",
            "ciudad_nombre": "La Plata",
            "categoria_nombre": "Plaza",
            "latitud": -34.9214,
            "longitud": -57.9544,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "1882-11-19",
            "fecha_registro": "2023-06-15",
        },
        {
            "nombre": "Estadio Monumental Antonio Vespucio Liberti",
            "descripcion": "Estadio de fútbol en Buenos Aires",
            "descripcion_completa": "Conocido como 'El Monumental', es el estadio más grande de Argentina y sede del club River Plate. También alberga partidos de la selección nacional.",
            "ciudad_nombre": "Buenos Aires",
            "categoria_nombre": "Estadio",
            "latitud": -34.5450,
            "longitud": -58.4497,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "1938-05-25",
            "fecha_registro": "2023-07-10",
        },
        {
            "nombre": "Obelisco de Buenos Aires",
            "descripcion": "Ícono histórico y cultural de la ciudad",
            "descripcion_completa": "Monumento emblemático ubicado en la Plaza de la República. Construido en 1936 para conmemorar el cuarto centenario de la fundación de la ciudad.",
            "ciudad_nombre": "Buenos Aires",
            "categoria_nombre": "Monumento",
            "latitud": -34.6037,
            "longitud": -58.3816,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "1936-05-23",
            "fecha_registro": "2023-08-05",
        },
        {
            "nombre": "Cementerio de la Recoleta",
            "descripcion": "Famoso cementerio histórico y turístico",
            "descripcion_completa": "Conocido por sus elaboradas bóvedas y mausoleos, es el lugar de descanso de muchas figuras históricas argentinas, incluyendo a Eva Perón.",
            "ciudad_nombre": "Buenos Aires",
            "categoria_nombre": "Cementerio",
            "latitud": -34.5881,
            "longitud": -58.3933,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "1822-11-17",
            "fecha_registro": "2023-09-12",
        },
        {
            "nombre": "Palacio Barolo",
            "descripcion": "Edificio histórico de estilo neogótico",
            "descripcion_completa": "Inspirado en la Divina Comedia de Dante Alighieri, este edificio es un ícono arquitectónico de Buenos Aires. Ofrece visitas guiadas y vistas panorámicas desde su cúpula.",
            "ciudad_nombre": "Buenos Aires",
            "categoria_nombre": "Edificio Histórico",
            "latitud": -34.6085,
            "longitud": -58.3700,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "1923-07-01",
            "fecha_registro": "2023-10-20",
        },
        {
            "nombre": "Plaza de Mayo",
            "descripcion": "Plaza histórica y centro político de Argentina",
            "descripcion_completa": "Lugar emblemático donde se han desarrollado importantes eventos históricos y políticos. Rodeada por edificios como la Casa Rosada y la Catedral Metropolitana.",
            "ciudad_nombre": "Buenos Aires",
            "categoria_nombre": "Plaza",
            "latitud": -34.6083,
            "longitud": -58.3700,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "1580-06-11",
            "fecha_registro": "2023-11-15",
        },
        {
            "nombre": "Avenida 9 de Julio",
            "descripcion": "Una de las avenidas más anchas del mundo",
            "descripcion_completa": "Avenida emblemática que atraviesa el centro de Buenos Aires. Conocida por su ancho y por albergar el Obelisco, es un punto neurálgico de la ciudad.",
            "ciudad_nombre": "Buenos Aires",
            "categoria_nombre": "Avenida",
            "latitud": -34.6037,
            "longitud": -58.3816,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "1937-03-19",
            "fecha_registro": "2023-12-01",
        },
        {
            "nombre": "Catedral Metropolitana de Buenos Aires",
            "descripcion": "Principal iglesia católica de Argentina",
            "descripcion_completa": "Imponente catedral de estilo neoclásico ubicada en la Plaza de Mayo. Es la sede del Arzobispado de Buenos Aires y un importante centro religioso.",
            "ciudad_nombre": "Buenos Aires",
            "categoria_nombre": "Edificio Histórico",
            "latitud": -34.6086,
            "longitud": -58.3702,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "1791-12-06",
            "fecha_registro": "2024-01-10",
        },
        {
            "nombre": "Puente de la Mujer",
            "descripcion": "Puente peatonal moderno en Puerto Madero",
            "descripcion_completa": "Diseñado por Santiago Calatrava, este puente giratorio es un ícono de la arquitectura moderna en Buenos Aires. Conecta las áreas de Puerto Madero y el centro de la ciudad.",
            "ciudad_nombre": "Buenos Aires",
            "categoria_nombre": "Puente",
            "latitud": -34.6080,
            "longitud": -58.3640,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "2001-12-20",
            "fecha_registro": "2024-02-18",
        },
        {
            "nombre": "Museo Nacional de Bellas Artes",
            "descripcion": "Principal museo de arte de Argentina",
            "descripcion_completa": "Alberga una vasta colección de arte argentino e internacional, incluyendo obras de artistas como Goya, Van Gogh y Rembrandt. Es un importante centro cultural.",
            "ciudad_nombre": "Buenos Aires",
            "categoria_nombre": "Museo",
            "latitud": -34.5889,
            "longitud": -58.3973,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "1895-12-25",
            "fecha_registro": "2024-03-05",
        },
        {
            "nombre": "Café Tortoni",
            "descripcion": "Café histórico y cultural de Buenos Aires",
            "descripcion_completa": "Fundado en 1858, es uno de los cafés más antiguos y emblemáticos de la ciudad. Ha sido punto de encuentro de artistas, escritores y figuras históricas.",
            "ciudad_nombre": "Buenos Aires",
            "categoria_nombre": "Café Histórico",
            "latitud": -34.6087,
            "longitud": -58.3730,
            "estado_conservacion": "Bueno",
            "fecha_inauguracion": "1858-07-01",
            "fecha_registro": "2024-04-12",
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
            "visible": item.get("visible", "True"),
            "baja": item.get("baja", "False"),
        }
        created.append(board.crear_sitio_seed(form_like))

    print("Seeded sitios:")
    for s in created:
        print(" ", s)

    print("Creating roles...")
    rol_admin = board.create_rol(nombre="Admin")
    rol_editor = board.create_rol(nombre="Editor")
    rol_user = board.create_rol(nombre="Usuario")
    print("Created roles! 👍🏻")

    print('Creando permisos..')
    
    PERMISSIONS = {
    'editor': [
        "site_index",
        "site_show",
        "site_new",
        "site_create",
        "site_edit",
        "site_update",
        "tag_index",
        "tag_show",
        "tag_new",
        "tag_create",
        "tag_edit",
        "tag_update",
        "tag_destroy",
        "record_show",
        "profile_show",
        "profile_update",
        "change_password",
    ],
    'admin': [
        "user_index",
        "user_show",
        "user_create",
        "user_new",
        "user_edit",
        "user_update",
        "user_destroy",
        "user_activate",
        "user_deactivate",
        "site_index",
        "site_show",
        "site_new",
        "site_create",
        "site_edit",
        "site_update",
        "site_destroy",
        "site_export",
        "tag_index",
        "tag_show",
        "tag_new",
        "tag_create",
        "tag_edit",
        "tag_update",
        "tag_destroy",
        "record_show",
        "profile_show",
        "profile_update",
        "change_password",
    ]
}
    auth.crearPermisos(PERMISSIONS)
    print('Permisos creados! 👍🏻')

    print("Creating users...")

    user1 = auth.create_user(
        nombre="Pepe",
        apellido="Argento",
        password="secreto",
        email="a@gmail.com",
        activo=True,
        esAdmin=False,
        roles=[rol_admin, rol_editor]
    )
    user2 = auth.create_user(
        nombre="Moni",
        apellido="Argento",
        password="secreto",
        email="b@gmail.com",
        activo=True,
        esAdmin=False,
        roles=[rol_admin, rol_editor]
    )
    user3 = auth.create_user(
        nombre="Coqui",
        apellido="Argento",
        password="secreto",
        email="c@gmail.com",
        activo=True,
        esAdmin=False,
        roles=[rol_admin, rol_editor]
    )

    user4 = auth.create_user(
        nombre="Paola",
        apellido="Argento",
        password="paola123",
        email="paola.a@gmail.com",
        activo=False,
        esAdmin=False,
        roles=[rol_admin, rol_editor]
    )

    user5 = auth.create_user(
        nombre="Dardo",
        apellido="Funes",
        password="dardo",
        email="dardo.f@empresa.com",
        activo=True,
        esAdmin=False,
        roles=[rol_admin]
    )

    user6 = auth.create_user(
        nombre="María",
        apellido="Elena",
        password="mariaelena",
        email="me.fuseneco@otro.com",
        activo=True,
        esAdmin=False,
        roles=[rol_editor]
    )

    user7 = auth.create_user(
        nombre="Elvira",
        apellido="Roca",
        password="elvira",
        email="elviraroca@gmail.com",
        activo=True,
        esAdmin=False,
        roles=[rol_admin]
    )

    user8 = auth.create_user(
        nombre="Roberto",
        apellido="Gómez",
        password="roberto",
        email="roberto.g@mail.com",
        activo=True,
        esAdmin=False,
        roles=[rol_admin]
    )

    user9 = auth.create_user(
        nombre="Ana",
        apellido="Pérez",
        password="ana123",
        email="ana.perez@dominio.net",
        activo=True,
        esAdmin=False,
        roles=[rol_editor]
    )

    user10 = auth.create_user(
        nombre="Carlos",
        apellido="López",
        password="carlos",
        email="carlos.l@empresa.com",
        activo=True,
        esAdmin=False,
        roles=[rol_admin]
    )

    user11 = auth.create_user(
        nombre="Laura",
        apellido="Martínez",
        password="laura456",
        email="laura.m@test.org",
        activo=False,
        esAdmin=False,
        roles=[rol_admin]
    )

    user12 = auth.create_user(
        nombre="Jorge",
        apellido="Rodríguez",
        password="jorge",
        email="jorge.r@system.io",
        activo=True,
        esAdmin=False,
        roles=[rol_admin]
    )

    user13 = auth.create_user(
        nombre="Sofía",
        apellido="Sánchez",
        password="sofia",
        email="sofia.s@newmail.co",
        activo=True,
        esAdmin=False,
        roles=[rol_editor]
    )

    user14 = auth.create_user(
        nombre="Martín",
        apellido="García",
        password="martin",
        email="martin.g@web.es",
        activo=True,
        esAdmin=False,
        roles=[rol_admin]
    )

    user15 = auth.create_user(
        nombre="Valentina",
        apellido="Diaz",
        password="valentina",
        email="v.diaz@mailserver.net",
        activo=True,
        esAdmin=False,
        roles=[rol_editor]
    )

    user16 = auth.create_user(
        nombre="Diego",
        apellido="Hernández",
        password="diego",
        email="d.h@pro.com",
        activo=True,
        esAdmin=False,
        roles=[rol_admin]
    )

    user17 = auth.create_user(
        nombre="Florencia",
        apellido="Ruiz",
        password="florencia",
        email="florencia.r@temp.net",
        activo=True,
        esAdmin=False,
        roles=[rol_admin]
    )

    user18 = auth.create_user(
        nombre="Emiliano",
        apellido="Castro",
        password="emiliano",
        email="emi.c@data.org",
        activo=False,
        esAdmin=False,
        roles=[rol_admin]
    )

    user19 = auth.create_user(
        nombre="Camila",
        apellido="Flores",
        password="camila",
        email="camila.f@work.co",
        activo=True,
        esAdmin=False,
        roles=[rol_editor]
    )

    user20 = auth.create_user(
        nombre="Lucas",
        apellido="Morales",
        password="lucas",
        email="lucas.m@mail.io",
        activo=True,
        esAdmin=False,
        roles=[rol_admin]
    )

    user21 = auth.create_user(
        nombre="Andrea",
        apellido="Vargas",
        password="andrea",
        email="andrea.v@sistema.com",
        activo=True,
        esAdmin=False,
        roles=[rol_admin]
    )

    user22 = auth.create_user(
        nombre="Federico",
        apellido="Blanco",
        password="federico",
        email="fede.b@email.net",
        activo=True,
        esAdmin=False,
        roles=[rol_editor]
    )

    user23 = auth.create_user(
        nombre="Gabriela",
        apellido="Ramos",
        password="gabriela",
        email="g.ramos@secure.org",
        activo=True,
        esAdmin=False,
        roles=[rol_admin]
    )

    user24 = auth.create_user(
        nombre="Hernán",
        apellido="Acosta",
        password="hernan",
        email="hernan.a@client.com",
        activo=False,
        esAdmin=False,
        roles=[rol_admin]
    )

    user25 = auth.create_user(
        nombre="Lautaro",
        apellido="Messi",
        password="secreto",
        email="lau@gmail.com",
        activo=False,
        esAdmin=False,
        roles=[rol_admin]
    )

    user26 = auth.create_user(
        nombre="Martin",
        apellido="Martinez",
        password="secreto",
        email="martin@gmail.com",
        activo=False,
        esAdmin=False,
        roles=[rol_admin]
    )

    print("Created users! 👍🏻")

