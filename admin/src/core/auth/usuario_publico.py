from src.core.database import Base
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Boolean, Integer, ForeignKey
from datetime import datetime, timezone
from src.core.entity.rol import Rol  
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Table, Column, UniqueConstraint

class UsuarioPublico(Base):
    __tablename__ = 'usuarios_publicos'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    foto: Mapped[str] = mapped_column(String(255), nullable=True)
    borradoLogico: Mapped[bool] = mapped_column(Boolean, default=False)
    fechaCreacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return (
            f"<Usuario(id={self.id}, "
            f"nombre={self.nombre}, "
            f"apellido={self.apellido}, "
            f"email={self.email}, "
            f"borradoLogico={self.borradoLogico}, "
            f"fechaCreacion={self.fechaCreacion}>"
        )
    
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email,
            "foto": self.foto
        }