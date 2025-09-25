from datetime import datetime
from src.core.database import db
from core.sitio import Sitio


def mostrar_sitios():
    sitios = db.session.query(Sitio).order_by(Sitio.id).filter_by(activo=True).all()
    return sitios


def agregar_sitioseed(**kwargs):
    nuevo_sitio = Sitio(**kwargs)
    db.session.add(nuevo_sitio)
    db.session.commit()

    return nuevo_sitio


def agregar_sitio(form):
    nuevo_sitio = Sitio(
        nombre=form.get("nombre"),
        descripcion=form.get("descripcion"),
        descripcion_completa=form.get("descripcion_completa"),
        ciudad=form.get("ciudad"),
        provincia=form.get("provincia"),
        ubicacion=form.get("ubicacion"),
        estado_conservacion=form.get("estado_conservacion"),
        fecha_inauguracion=datetime.strptime(form.get("fecha_inauguracion"), "%Y-%m-%d") if form.get("fecha_inauguracion") else None,
        categoria=form.get("categoria"),
        fecha_registro=datetime.strptime(form.get("fecha_registro"), "%Y-%m-%d") if form.get("fecha_registro") else None,
        visible=True if form.get("visible") == "True" else False
    )
    db.session.add(nuevo_sitio)
    db.session.commit()
    return nuevo_sitio

def obtener_sitio(sitio_id):
    sitio = db.session.get(Sitio, sitio_id)
    return sitio


def editar_sitio(sitio_id, form):
    sitio = obtener_sitio(sitio_id)
    if sitio:
        sitio.nombre=form.get("nombre"),
        sitio.descripcion=form.get("descripcion"),
        sitio.descripcion_completa=form.get("descripcion_completa"),
        sitio.ciudad=form.get("ciudad"),
        sitio.provincia=form.get("provincia"),
        sitio.ubicacion=form.get("ubicacion"),
        sitio.estado_conservacion=form.get("estado_conservacion"),
        sitio.fecha_inauguracion=datetime.strptime(form.get("fecha_inauguracion"), "%Y-%m-%d") if form.get("fecha_inauguracion") else None,
        sitio.categoria=form.get("categoria"),
        sitio.fecha_registro=datetime.strptime(form.get("fecha_registro"), "%Y-%m-%d") if form.get("fecha_registro") else None,
        sitio.visible=True if form.get("visible") == "True" else False
        db.session.commit()
        return True
    return False


def eliminar_sitio(sitio_id):
    sitio = obtener_sitio(sitio_id)
    if sitio:
        sitio.activo = False
        db.session.commit()
        return True
    else:
        return False


