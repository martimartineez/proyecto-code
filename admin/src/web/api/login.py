from flask import Blueprint, request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests



bp = Blueprint('login', __name__, url_prefix='/api/login')

@bp.route('/google', methods=['POST', 'OPTIONS'])
def login_google():
    if request.method == "OPTIONS":
        return {}, 200

    data = request.get_json()
    token = data.get("token")

    try:
        info = id_token.verify_oauth2_token(token, requests.Request(), "501426149813-3ldbtlaur9oodqe8eq5rhuqrecjn22s7.apps.googleusercontent.com")

        # info["email"], info["name"], info["sub"], etc.
        return jsonify({
            "success": True,
            "user": {
                "email": info["email"],
                "name": info.get("name")
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400