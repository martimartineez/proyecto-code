from src.core.database import db
from src.core.auth.usuario import Usuario
from src.core.board.rol import Rol


def list_usuarios():
    #return db.session.query(Usuario.nombre, Usuario.email).all()
    return db.session.query(Usuario).all()

    
def delete_user(user: Usuario):
    db.session.delete(user)
    db.session.commit()

def create_user(**kwargs):
    user = Usuario(**kwargs)
    db.session.add(user)
    db.session.commit()

    return user

def get_user_by_id(user_id):
    return db.session.query(Usuario).filter(Usuario.id == user_id).first()

def find_user(email, password):
    return db.session.query(Usuario).filter(Usuario.email == email, Usuario.password == password).first()

def baja_logica_usuario(user: Usuario):
    user.activo = False
    db.session.commit()
    return user
