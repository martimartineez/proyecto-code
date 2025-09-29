from src.core.database import db
from src.core.auth.usuario import Usuario
from src.core.board.rol import Rol


def list_usuarios():
    #return db.session.query(Usuario.nombre, Usuario.email).all()
    return db.session.query(Usuario).all()

    


def create_user(**kwargs):
    user = Usuario(**kwargs)
    db.session.add(user)
    db.session.commit()

    return user
