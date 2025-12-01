from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base


class SitioImagen(Base):
    __tablename__ = "sitios_imagenes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_sitio: Mapped[int] = mapped_column(
        Integer, ForeignKey("sitios_historicos.id"), nullable=False
    )

    # URL pública al archivo y nombre del objeto en MinIO
    url_publica: Mapped[str] = mapped_column(String(512), nullable=False)
    object_name: Mapped[str] = mapped_column(String(512), nullable=False)

    titulo_alt: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Orden y portada
    orden: Mapped[int] = mapped_column(Integer, default=0)
    portada: Mapped[bool] = mapped_column(Boolean, default=False)

    inserted_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    sitio: Mapped["SitioHistorico"] = relationship(
        "SitioHistorico", back_populates="imagenes"
    )
