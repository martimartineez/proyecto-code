from flask import flash
from src.core.database import db
from src.core.auth.usuario import Usuario
from src.core.board.rol import Rol
from datetime import datetime


def list_usuarios():
    #return db.session.query(Usuario.nombre, Usuario.email).all()
    return db.session.query(Usuario).all()

    
def delete_user(user: Usuario):
    db.session.delete(user)
    db.session.commit()

def crear_usuario(form):
    from src.core.board import _parse_date, _parse_int
    if(comprobar_email(form.get("email"))):
        flash("El mail ingresado ya esta registrado, por favor ingrese otro", "info")
        return False
    else:
        nuevo = Usuario(
            nombre=form.get("nombre"),
            apellido=form.get("apellido"),
            password=form.get("password"),
            email=form.get("email"),
            activo=True,    
            fechaCreacion=_parse_date( datetime.now()),
            idRol=_parse_int(1 if form.get("rol") == "admin" else 2),
            esAdmin=True if form.get("rol") == "admin" else False,
        )
        db.session.add(nuevo)
        db.session.commit()
        return True

def comprobar_email(email: str):
    usuario = db.session.query(Usuario).filter(Usuario.email == email).first()
    return True if usuario else False

def get_user_by_id(user_id):
    return db.session.query(Usuario).filter(Usuario.id == user_id).first()

def baja_logica_usuario(user: Usuario):
    user.activo = False
    db.session.commit()
    return user
