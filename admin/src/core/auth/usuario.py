from src.core.database import Base
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Boolean, Integer, ForeignKey
from datetime import datetime, timezone
from src.core.entity.rol import Rol  
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Table, Column, UniqueConstraint
from sqlalchemy import func

if TYPE_CHECKING:
    from src.core.entity.rol import Rol


roles_usuarios = Table(
    "roles_usuarios",
    Base.metadata,
    Column("usuarioId", ForeignKey("usuarios.id"), primary_key=True),
    Column("rolId", ForeignKey("roles.id"), primary_key=True),
)

favoritos_usuarios_sitios = Table(
    "favoritos_usuarios_sitios",
    Base.metadata,
    Column("usuario_id", ForeignKey("usuarios.id"), primary_key=True),
    Column("sitio_id", ForeignKey("sitios_historicos.id"), primary_key=True),

    Column("inserted_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now(), nullable=False),

    UniqueConstraint("usuario_id", "sitio_id", name="unique_user_site_favorite"),
)

class Usuario(Base):
    __tablename__ = 'usuarios'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=True)
    password: Mapped[str] = mapped_column(String(100), nullable=True) #puse nullable true para usuarios publicos
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    esAdmin: Mapped[bool] = mapped_column(Boolean, default=False)
    borradoLogico: Mapped[bool] = mapped_column(Boolean, default=False)
    fechaCreacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    roles: Mapped[List["Rol"]] = relationship(
        secondary=roles_usuarios,
        back_populates='usuario'
    )
    favoritos: Mapped[List["SitioHistorico"]] = relationship(
        secondary=favoritos_usuarios_sitios,
        back_populates="favorited_by"
    )
    foto: Mapped[str] = mapped_column(String(255), nullable=True)
    publico: Mapped[bool] = mapped_column(Boolean, default=False)




    def __repr__(self):
        return (
            f"<Usuario(id={self.id}, "
            f"nombre={self.nombre}, "
            f"apellido={self.apellido}, "
            f"password={self.password}, "
            f"email={self.email}, "
            f"activo={self.activo}, esAdmin={self.esAdmin}, "
            f"borradoLogico={self.borradoLogico}, "
            f"fechaCreacion={self.fechaCreacion}, idRol={getattr(self, 'idRol', None)})>"
        )
    
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email,
            "foto": self.foto
        }
    
