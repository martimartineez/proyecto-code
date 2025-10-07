from src.core.database import Base
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Boolean, Integer, ForeignKey
from datetime import datetime, timezone
from src.core.board.rol import Rol  
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Table, Column

if TYPE_CHECKING:
    from src.core.board.rol import Rol


roles_usuarios = Table(
    "roles_usuarios",
    Base.metadata,
    Column("usuarioId", ForeignKey("usuarios.id"), primary_key=True),
    Column("rolId", ForeignKey("roles.id"), primary_key=True),
)

class Usuario(Base):
    __tablename__ = 'usuarios'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    esAdmin: Mapped[bool] = mapped_column(Boolean, default=False)
    borradoLogico: Mapped[bool] = mapped_column(Boolean, default=False)
    fechaCreacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    roles: Mapped[List["Rol"]] = relationship(
        secondary=roles_usuarios,
        back_populates='usuario'
    )

    # sitios: Mapped[List["SitioHistorico"]] = relationship(
    #     secondary=tags_sitios,
    #     back_populates="tags",
    # )

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
    
