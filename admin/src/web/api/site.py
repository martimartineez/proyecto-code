from flask import Blueprint, request, jsonify



bp = Blueprint('site_api', __name__, url_prefix='/api/sites')

@bp.route('', methods=['GET'])
def list_sites():
