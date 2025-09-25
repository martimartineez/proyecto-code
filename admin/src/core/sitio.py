from src.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from sqlalchemy import DateTime


class Sitio(Base):
    __tablename__ = "sitios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(nullable=False)
    descripcion: Mapped[str] = mapped_column(nullable=True)
    descripcion_completa: Mapped[str] = mapped_column(nullable=True)
    ciudad: Mapped[str] = mapped_column(nullable=False)
    provincia: Mapped[str] = mapped_column(nullable=False)
    ubicacion: Mapped[str] = mapped_column(nullable=True)
    estado_conservacion: Mapped[str] = mapped_column(nullable=False)
    fecha_inauguracion: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    categoria: Mapped[str] = mapped_column(nullable=False)
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    visible: Mapped[bool] = mapped_column(nullable=False, default=True)

    activo: Mapped[bool] = mapped_column(nullable=False, default=True)

    inserted_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<Issue(id={self.id}, title='{self.nombre}', status='{self.visible}')>"
