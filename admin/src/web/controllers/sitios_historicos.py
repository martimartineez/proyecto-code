from core import board
from flask import Blueprint, render_template, request, redirect, url_for

bp = Blueprint('sitios_historicos', __name__, url_prefix='/sitioshistoricos')

@bp.get('/')
def index():
    sitios_historicos = board.mostrar_sitios()
    return render_template('sitios_historicos/index.html', sitios=sitios_historicos)

@bp.route('/nuevo', methods=['GET', 'POST'])
def agregar_sitio():
    if request.method == 'POST':
        # Procesar datos y agregar sitio
        board.agregar_sitio(request.form)
        return redirect(url_for('sitios_historicos.index'))
    return render_template('sitios_historicos/formAgregar.html')

@bp.route('/<int:sitio_id>/editar', methods=['GET', 'POST'])
def editar_sitio(sitio_id):
    if request.method == 'POST':
        # Procesar edición
        print("formulario si")
        board.editar_sitio(sitio_id, request.form)
        return redirect(url_for('sitios_historicos.index'))
    sitio = board.obtener_sitio(sitio_id)
    return render_template('sitios_historicos/formEditar.html', sitio=sitio)

@bp.post('/<int:sitio_id>/eliminar')
def eliminar_sitio(sitio_id):
    board.eliminar_sitio(sitio_id)
    return redirect(url_for('sitios_historicos.index'))