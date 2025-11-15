from re import U
from flask import Blueprint
from flask import render_template, request, redirect, url_for, flash, session
from src.core import auth
from src.core.entity.services import feature_flags as ff_service
from src.web.handlers.auth import is_system_admin

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
    if auth.comprobar_bloqueado(user) == False:
        flash('Usuario bloqueado, contacte al administrador', 'error')
        return redirect(url_for('auth.login'))
    # Si el panel está en mantenimiento admin, sólo administradores (esAdmin=True) pueden iniciar sesión
    flag = ff_service.get_flag('admin_maintenance_mode')
    if flag and flag.valor:
        if not getattr(user, 'esAdmin', False):
            msg = flag.mensaje or 'Sistema en mantenimiento.'
            flash(msg, 'error')
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