from flask_sqlalchemy_lite import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

db = SQLAlchemy()


def init_db(app):

    db.init_app(app)

    return db


def reset_db():
    from src.core.board.permiso import Permiso
    from src.core.board.rol import Rol, roles_permisos  # noqa: F401
    from src.core.auth.usuario import Usuario  # noqa: F401
    from src.core.board.sitio_historico import SitioHistorico  # noqa: F401
    from src.core.board.tag import Tag, tags_sitios  # noqa: F401
    from src.core.board.categoria_sitio import CategoriaSitio  # noqa: F401
    from src.core.board.provincia import Provincia  # noqa: F401
    from src.core.board.ciudad import Ciudad  # noqa: F401
    from src.core.board.feature_flag import FeatureFlag  # noqa: F401
    from src.core.board.historial_sitio import HistorialSitio  # noqa: F401
    from src.core.board.seeds import seed_geografia, seed_categorias

    Base.metadata.drop_all(bind=db.engine)
    Base.metadata.create_all(bind=db.engine)
    print("reset successfully")
    # Seed initial Provincias and Ciudades
    seed_geografia()
    # Seed initial Categorias
    seed_categorias()


class Base(DeclarativeBase):
    pass
