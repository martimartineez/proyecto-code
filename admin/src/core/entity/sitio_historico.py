from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, Date, DateTime, Float, ForeignKey, Text
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base

if TYPE_CHECKING:
    from src.core.entity.tag import Tag
    from src.core.entity.categoria_sitio import CategoriaSitio
    from src.core.entity.ciudad import Ciudad


class SitioHistorico(Base):
    __tablename__ = "sitios_historicos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    descBreve: Mapped[str | None] = mapped_column(String(255), nullable=True)
    descCompleta: Mapped[str | None] = mapped_column(Text, nullable=True)
    idCiudad: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("ciudades.id"), nullable=True
    )
    ciudad: Mapped[Ciudad | None] = relationship("Ciudad", back_populates="sitios")

    latitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitud: Mapped[float | None] = mapped_column(Float, nullable=True)

    estadoConservacion: Mapped[str | None] = mapped_column(String(50), nullable=True)
    anioInauguracion: Mapped[Date | None] = mapped_column(Date, nullable=True)

    idCategoria: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categorias_sitios.id"), nullable=True
    )
    categoria: Mapped[CategoriaSitio | None] = relationship(
        "CategoriaSitio", back_populates="sitios"
    )

    fechaRegistro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    visible: Mapped[bool] = mapped_column(Boolean, default=True)
    baja: Mapped[bool] = mapped_column(Boolean, default=False)

    tags: Mapped[List["Tag"]] = relationship(
        secondary="tags_sitios",
        back_populates="sitios",
    )

    inserted_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


    def __repr__(self):
        return (
            f"<SitioHistorico(id={self.id}, nombre={self.nombre}, ciudad={self.ciudad}, "
            f"latitud={self.latitud}, longitud={self.longitud}, baja={self.baja})>"
        )
