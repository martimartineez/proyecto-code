sitios = [
        {
            "id": 1,
            "nombre": "Parque Central",
            "descripcion": "Un parque grande con áreas verdes y un lago.",
            "descripcion_completa": "El Parque Central es un espacio ideal para actividades al aire libre, picnics y paseos en bote por el lago.",
            "ciudad": "Ciudad A",
            "provincia": "Provincia A",
            "ubicacion": {"latitud": 40.7128, "longitud": -74.0060},
            "estado_conservacion": "Bueno",
            "anio_fundacion": 1950,
            "categoria": "Parque",
            "fecha_registro": "2020-01-15",
            "visible": True,
        },
        {
            "id": 2,
            "nombre": "Museo de Arte",
            "descripcion": "Un museo con una colección impresionante de arte moderno.",
            "descripcion_completa": "El Museo de Arte alberga obras de artistas contemporáneos y ofrece exposiciones temporales y talleres educativos.",
            "ciudad": "Ciudad B",
            "provincia": "Provincia B",
            "ubicacion": {"latitud": 34.0522, "longitud": -118.2437},
            "estado_conservacion": "Excelente",
            "anio_fundacion": 1985,
            "categoria": "Museo",
            "fecha_registro": "2019-11-30",
            "visible": True,
        },
        {
            "id": 3,
            "nombre": "Playa Dorada",
            "descripcion": "Una playa hermosa con arena dorada y aguas cristalinas.",
            "descripcion_completa": "Playa Dorada es perfecta para nadar, tomar el sol y practicar deportes acuáticos. Cuenta con servicios de alquiler de equipos y restaurantes cercanos.",
            "ciudad": "Ciudad C",
            "provincia": "Provincia C",
            "ubicacion": {"latitud": 25.7617, "longitud": -80.1918},
            "estado_conservacion": "Muy Bueno",
            "anio_fundacion": 1975,
            "categoria": "Playa",
            "fecha_registro": "2021-06-20",
            "visible": True,
        },
        {
            "id": 4,
            "nombre": "Catedral de la Ciudad",
            "descripcion": "Una catedral histórica con arquitectura impresionante.",
            "descripcion_completa": "La Catedral de la Ciudad es un monumento emblemático que data del siglo XVIII, conocida por sus vitrales y su altar barroco.",
            "ciudad": "Ciudad D",
            "provincia": "Provincia D",
            "ubicacion": {"latitud": 51.5074, "longitud": -0.1278},
            "estado_conservacion": "Excelente",
            "anio_fundacion": 1720,
            "categoria": "Monumento",
            "fecha_registro": "2018-09-10",
            "visible": False,
        },
        {
            "id": 5,
            "nombre": "Reserva Natural El Bosque",
            "descripcion": "Una reserva natural con senderos para caminatas y observación de aves.",
            "descripcion_completa": "La Reserva Natural El Bosque ofrece una experiencia única para los amantes de la naturaleza, con una gran diversidad de flora y fauna.",
            "ciudad": "Ciudad E",
            "provincia": "Provincia E",
            "ubicacion": {"latitud": 48.8566, "longitud": 2.3522},
            "estado_conservacion": "Bueno",
            "anio_fundacion": 1990,
            "categoria": "Reserva Natural",
            "fecha_registro": "2022-03-05",
            "visible": True,
        },
    ]

def mostrar_sitios():
    return sitios

def agregar_sitio(form):
    nuevo_id = len(sitios) + 1
    sitio = {
        "id": nuevo_id,
        "nombre": form.get("nombre"),
        "descripcion": form.get("descripcion"),
        "descripcion_completa": form.get("descripcion_completa"),
        "ciudad": form.get("ciudad"),
        "provincia": form.get("provincia"),
        "ubicacion": {
            "latitud": float(form.get("latitud", 0)),
            "longitud": float(form.get("longitud", 0)),
        },
        "estado_conservacion": form.get("estado_conservacion"),
        "anio_fundacion": int(form.get("anio_fundacion", 0)),
        "categoria": form.get("categoria"),
        "fecha_registro": form.get("fecha_registro"),
        "visible": form.get("visible") == "True",
    }
    sitios.append(sitio)

def obtener_sitio(sitio_id):
    for sitio in sitios:
        if sitio['id'] == sitio_id:
            return sitio
    return None

def editar_sitio(sitio_id, form):
    sitio = obtener_sitio(sitio_id)
    if sitio:
        sitio.update(form)
        # El id no se modifica
        actualizar_sitios(sitio, sitio_id)
        return True
    return False

def eliminar_sitio(sitio_id):
    global sitios
    sitios = [s for s in sitios if s['id'] != sitio_id]
    return True

def actualizar_sitios(sitioCambiado, id):
    global sitios
    for sitio in sitios:
        if sitio['id'] == id:
            sitio.update(sitioCambiado)
    return True