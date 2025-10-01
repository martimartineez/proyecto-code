from functools import wraps
from flask import session, redirect, url_for, flash


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

