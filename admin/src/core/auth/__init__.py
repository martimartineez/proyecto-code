from src.core.database import db
from src.core.auth.usuario import Usuario
from src.core.board.rol import Rol
from src.core.bcrypt import bcrypt



def crearPermisos(permisos):
    from src.core.board.rol import Rol
    from src.core.board.permiso import Permiso
    #Creo los nuevos permisos
    admin = db.session.query(Rol).filter(Rol.nombre == "Admin").first()
    editor = db.session.query(Rol).filter(Rol.nombre == "Editor").first()
    for permiso in permisos["admin"]:
        admin.permisos.append(Permiso(nombre=permiso))
    for permiso in permisos["editor"]:
        editor.permisos.append(Permiso(nombre=permiso))
    db.session.commit()
    return True

def permissions(user):
    permisos = db.session.query(Rol).filter(Rol.id == user.idRol).first().permisos
    nombres_permisos = [permiso.nombre for permiso in permisos]
    return nombres_permisos

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

def update_password(usuario_id, new_password):
    user = get_user_by_id(usuario_id)
    hash_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    user.password = hash_password
    db.session.commit()
    return user

def get_user_by_id(user_id):
    return db.session.query(Usuario).filter(Usuario.id == user_id).first()

def find_user(email):
    return db.session.query(Usuario).filter(Usuario.email == email).first()

def check_user(email,password):
    user = find_user(email)
    if user and check_password(user,password):
        return user
    return None

def check_password(user,password):
    return bcrypt.check_password_hash(user.password, password)


def comprobar_email(email: str):
    usuario = db.session.query(Usuario).filter(Usuario.email == email).first()
    return True if usuario else False


def baja_logica_usuario(user: Usuario):
    user.activo = False
    db.session.commit()
    return user


