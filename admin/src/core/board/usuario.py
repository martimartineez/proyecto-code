from src.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Boolean, Integer, ForeignKey
from datetime import datetime, timezone

class Usuario(Base):
    __tablename__ = 'usuarios'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    esAdmin: Mapped[bool] = mapped_column(Boolean, default=False)
    fechaCreacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    idRol: Mapped[int] = mapped_column(Integer, ForeignKey('roles.id'), nullable=False)

    def __repr__(self):
        return f"<Usuario(id={self.id}, nombre={self.nombre}, apellido={self.apellido}, password={self.password}, email={self.email}, activo={self.activo}, esAdmin={self.esAdmin}, fechaCreacion={self.fechaCreacion}, idRol={self.idRol})>"