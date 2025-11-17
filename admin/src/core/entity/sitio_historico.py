from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, Date, DateTime, Float, ForeignKey, Text
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base
from src.core.auth.usuario import favoritos_usuarios_sitios

from collections import OrderedDict
if TYPE_CHECKING:
    from src.core.entity.tag import Tag
    from src.core.entity.categoria_sitio import CategoriaSitio
    from src.core.entity.ciudad import Ciudad
    from src.core.entity.sitio_imagen import SitioImagen

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

    # Relación con imágenes del sitio
    imagenes: Mapped[List["SitioImagen"]] = relationship(
        "SitioImagen",
        back_populates="sitio",
        cascade="all, delete-orphan",
        order_by="SitioImagen.orden",
    )

    inserted_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    favorited_by: Mapped[List["Usuario"]] = relationship(
    secondary=favoritos_usuarios_sitios,
    back_populates="favoritos"
)


    def __repr__(self):
        return (
            f"<SitioHistorico(id={self.id}, nombre={self.nombre}, ciudad={self.ciudad}, "
            f"latitud={self.latitud}, longitud={self.longitud}, baja={self.baja})>"
        )
    def to_dict(self):
        d = OrderedDict()
        d["id"] = self.id
        d["name"] = self.nombre
        d["short_description"] = self.descBreve
        d["description"] = self.descCompleta
        d["city"] = self.ciudad.nombre if self.ciudad else None
        d["province"] = self.ciudad.provincia.nombre if self.ciudad and self.ciudad.provincia else None
        d["lat"] = self.latitud
        d["long"] = self.longitud
        d["tags"] = [t.nombre for t in self.tags]
        # URL de portada si existe
        try:
            portada = next((img for img in getattr(self, "imagenes", []) if getattr(img, "portada", False)), None)
            d["cover_url"] = portada.url_publica if portada else None
        except Exception:
            d["cover_url"] = None
        d["state_of_conservation"] = self.estadoConservacion
        d["inserted_at"] = self.inserted_at.isoformat() if self.inserted_at else None
        d["updated_at"] = self.updated_at.isoformat() if self.updated_at else None
        return d

