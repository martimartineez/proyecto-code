from src.core.database import db
from src.core.auth.usuario import Usuario
from src.core.board.rol import Rol
from src.core.bcrypt import bcrypt


def list_usuarios():
    #return db.session.query(Usuario.nombre, Usuario.email).all()
    return db.session.query(Usuario).all()

    
def delete_user(user: Usuario):
    db.session.delete(user)
    db.session.commit()

def create_user(**kwargs):
    hash_password = bcrypt.generate_password_hash(kwargs['password']).decode('utf-8')
    kwargs['password'] = hash_password

    user = Usuario(**kwargs)
    db.session.add(user)
    db.session.commit()

    return user

def get_user_by_id(user_id):
    return db.session.query(Usuario).filter(Usuario.id == user_id).first()

def find_user(email):
    return db.session.query(Usuario).filter(Usuario.email == email).first()

def check_user(email,password):
    user = find_user(email)
    if user and bcrypt.check_password_hash(user.password, password):
        return user
    return None



def baja_logica_usuario(user: Usuario):
    user.activo = False
    db.session.commit()
    return user
