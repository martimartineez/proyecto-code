from src.core.database import db
from core.sitio import Sitio



def mostrar_sitios():
    sitios = db.session.query(Sitio).all()
    return sitios


def agregar_sitio(**kwargs):
    nuevo_sitio = Sitio(**kwargs)
    db.session.add(nuevo_sitio)
    db.session.commit()

    return nuevo_sitio


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