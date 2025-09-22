from flask import Flask,send_file
from flask import render_template
from src.web.handlers import error
from src.web.config import config
from src.core import database
from src.csv.csv_utils import csv_exporter
import io

def create_app(env="development", static_folder = "../../static"):
    app = Flask(__name__, static_folder = static_folder)
    app.config.from_object(config[env])
    
    database.init_db(app)

    @app.route('/')
    def home():
        return render_template('home.html')
    
    @app.route('/exportarcsv')
    def exportar():
        data = [
        {"Nombre":"Lugar1","Descripcion":"Desc1","Ciudad":"C1","Provincia":"P1","Estado":"Activo","FechaRegistro":"2025-09-17","Coordenadas":"0,0","Tags":"tag1"},
        {"Nombre":"Lugar2","Descripcion":"Desc2","Ciudad":"C2","Provincia":"P2","Estado":"Inactivo","FechaRegistro":"2025-09-17","Coordenadas":"1,1","Tags":"tag2"}
        ]
        output = csv_exporter(data)
        return send_file(
            io.BytesIO(output.getvalue().encode("utf-8")),
            mimetype="text/csv",
            as_attachment=True,
            download_name="texto.csv"
    )

    
    app.register_error_handler(404, error.not_found)
    app.register_error_handler(401, error.unauthorized) 
    app.register_error_handler(500, error.server_error)

    return app