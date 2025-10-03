from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base

if TYPE_CHECKING:
    from .provincia import Provincia
    from .sitio_historico import SitioHistorico


class Ciudad(Base):
    __tablename__ = "ciudades"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)

    idProvincia: Mapped[int] = mapped_column(
        Integer, ForeignKey("provincias.id"), nullable=False
    )
    provincia: Mapped["Provincia"] = relationship(back_populates="ciudades")

    sitios: Mapped[list["SitioHistorico"]] = relationship(back_populates="ciudad")

    def __repr__(self):
        return f"<Ciudad(id={self.id}, nombre={self.nombre}, idProvincia={self.idProvincia})>"
