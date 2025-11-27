from flask import jsonify
from src.core.entity.services.feature_flags import get_flag
from flask import Blueprint

bp = Blueprint("feature_flags_api", __name__, url_prefix="/api")

@bp.route('/feature-flags/<flag_name>', methods=['GET'])
def get_feature_flag(flag_name):

    flag = get_flag(flag_name)
    if not flag:
        return jsonify({
            'error': f'Flag {flag_name} not found',
            'activo': False
        }), 404
        
    return jsonify({
        'nombre': flag.nombre,
        'descripcion': flag.descripcion,
        'activo': flag.valor,
        'mensaje': flag.mensaje
    })
