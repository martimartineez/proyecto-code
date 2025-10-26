from functools import wraps
from flask import session, redirect, url_for, flash, abort
from src.core import auth

def is_autenticated(session):
    return session.get('user') is not None


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_autenticated(session):
            flash('Debe iniciar sesión para acceder a esta página', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def check_permission(permission):
    # Los administradores del sistema (esAdmin=True) pasan cualquier verificación
    try:
        if is_system_admin():
            return True
    except Exception:
        pass
    user_email = session.get("user")
    user = auth.find_user(user_email)
    permissions = auth.permissions(user)
    return user is not None and permission in permissions


def check(permission):
    def decorator(f):
        @wraps(f)
        def decorated_funtion(*args, **kwargs):
            if not check_permission(permission):
                return abort(403)
            return f(*args, **kwargs)
        return decorated_funtion
    return decorator


def is_system_admin() -> bool:
    """Devuelve True si el usuario autenticado tiene esAdmin=True.
    Lee la sesión internamente (user_id o email) y consulta la entidad Usuario.
    """
    uid = session.get('user_id')
    user = None
    if uid:
        try:
            user = auth.get_user_by_id(uid)
        except Exception:
            user = None
    if not user:
        user_email = session.get("user")
        if user_email:
            user = auth.find_user(user_email)
    return bool(user and getattr(user, 'esAdmin', False))