from flask import Blueprint
from flask import render_template, request, redirect, url_for, flash, session
from src.core import auth

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.get('/')
def login():
    return render_template('manejo_usuarios/login.html')

@bp.post('/authenticate')
def authenticate():
    params = request.form
    user = auth.check_user(params['email'], params['password'])
    if not user:
        flash('Usuario o contraseña incorrecto/a', 'error')
        return redirect(url_for('auth.login'))
    
    session['user'] = user.email
    session['user_id'] = user.id
    session['username'] = user.nombre
    flash('Inicio de sesión exitoso', 'success')
    return redirect('/')

@bp.get('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        session.clear()
        flash('Cierre de sesión exitoso', 'success')
    else:
        flash('No hay una sesión activa', 'error')
    return redirect(url_for('auth.login'))