from __future__ import annotations
from typing import List, TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base

if TYPE_CHECKING:
    from .sitio_historico import SitioHistorico


class CategoriaSitio(Base):
    __tablename__ = "categorias_sitios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)

    sitios: Mapped[List["SitioHistorico"]] = relationship(back_populates="categoria")

    def __repr__(self):
        return f"<CategoriaSitio(id={self.id}, nombre={self.nombre})>"
