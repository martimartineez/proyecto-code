from functools import wraps
from flask import session, redirect, url_for, flash
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
    user_email = session.get("user")
    user = auth.find_user(user_email)
    permissions = auth.permissions(user)
    
    return user is not None and permission in permissions
