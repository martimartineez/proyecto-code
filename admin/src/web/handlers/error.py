from dataclasses import dataclass
from flask import render_template


@dataclass
class HTTPError:
    code: int
    message: str
    description: str


def forbidden(e):
    error = HTTPError(
        code=403,
        message="Acceso denegado",
        description="No cuentas con los permisos para acceder a esta pagina",
    )
    return render_template("error.html", error=error), 403


def not_found(e):
    error = HTTPError(
        code=404,
        message="Pagina no encontrada",
        description="Lo sentimos, la pagina que estas buscando no existe",
    )
    return render_template("error.html", error=error), 404


def unauthorized(e):
    error = HTTPError(
        code=401,
        message="Error de autenticacion",
        description="Lo sentimos, no tienes permisos para acceder a esta pagina",
    )
    return render_template("error.html", error=error), 401


def server_error(e):
    error = HTTPError(
        code=500,
        message="Error interno del servidor",
        description="Lo sentimos, el servidor encontro un error inesperado",
    )
    return render_template("error.html", error=error), 500
