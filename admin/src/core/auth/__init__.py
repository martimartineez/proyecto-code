from src.core.database import db
from src.core.auth.usuario import Usuario
from src.core.entity.rol import Rol
from src.core.bcrypt import bcrypt
from src.core.entity import services
from src.core.auth.usuario_publico import UsuarioPublico





def crearPermisos(permisos):
    from src.core.entity.rol import Rol
    from src.core.entity.permiso import Permiso
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
    permisos_usuario = list({permiso.nombre for rol in user.roles for permiso in rol.permisos})
    return permisos_usuario

def listar_roles_usuario(user):
    roles_usuario = list({rol.nombre for rol in user.roles})
    return roles_usuario


def list_usuarios():
    return db.session.query(Usuario).all()
    
def delete_user(user: Usuario):
    db.session.delete(user)
    db.session.commit()

def create_user(**kwargs):
    # Soporte idRol (legacy) para asignar un único rol inicial
    rol_id = None
    if 'idRol' in kwargs and kwargs['idRol'] is not None:
        try:
            rol_id = int(kwargs.pop('idRol'))
        except Exception:
            # si viene por nombre, intentamos resolverlo por nombre
            nombre_rol = kwargs.pop('idRol')
            rol = db.session.query(Rol).filter(Rol.nombre == nombre_rol).first()
            rol_id = rol.id if rol else None
    
    if 'password' in kwargs and kwargs['password'] is not None:
        hash_password = bcrypt.generate_password_hash(kwargs['password']).decode('utf-8')
        kwargs['password'] = hash_password

    user = Usuario(**kwargs)
    db.session.add(user)
    db.session.flush()

    if rol_id:
        rol = db.session.query(Rol).filter(Rol.id == rol_id).first()
        if rol and rol not in user.roles:
            user.roles.append(rol)

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
    user.borradoLogico = True
    db.session.commit()
    return user

def comprobar_bloqueado(user):
    estado = user.activo
    return estado

def crear_usuario_publico(nombre, apellido, email, foto):
    if not checkear_usuario_publico_existente(email):
        usuario_publico = UsuarioPublico(
            nombre=nombre,
            apellido=apellido,
            email=email,
            foto=foto,
        )
        db.session.add(usuario_publico)
        db.session.commit()
        return usuario_publico
    

def checkear_usuario_publico_existente(email):
    usuario = db.session.query(Usuario).filter(Usuario.email == email).first()
    return True if usuario else False

def devolver_usuario_publico_por_email(email):
    usuario = db.session.query(Usuario).filter(Usuario.email == email).first()
    return usuario

def actualizar_usuario_publico(email, info):   
    usuario = devolver_usuario_publico_por_email(email)
    if info.get("given_name") != usuario.nombre:
        usuario.nombre = info.get("given_name")
    if info.get("family_name") != usuario.apellido:
        usuario.apellido = info.get("family_name")
    if info.get("picture") != usuario.foto:
        usuario.foto = info.get("picture")
    db.session.commit()
    return usuario