from typing import List, TYPE_CHECKING
from src.core.database import Base
from src.core.entity.permiso import Permiso
#from src.core.auth.usuario import Usuario
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Table, Column

if TYPE_CHECKING:
    from src.core.auth.usuario import Usuario

roles_permisos = Table(
    "roles_permisos",
    Base.metadata,
    Column("permisoId", ForeignKey("permisos.id"), primary_key=True),
    Column("rolId", ForeignKey("roles.id"), primary_key=True),
)




class Rol(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    permisos: Mapped[List["Permiso"]] = relationship(secondary=roles_permisos)
    usuario: Mapped[List["Usuario"]] = relationship(
        secondary="roles_usuarios",
        back_populates='roles'
    )

    def __repr__(self):
        return f"<Rol(id={self.id}, nombre={self.nombre})>"
