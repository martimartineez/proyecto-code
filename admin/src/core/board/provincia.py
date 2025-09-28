from __future__ import annotations
from typing import List, TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base

if TYPE_CHECKING:
    from .ciudad import Ciudad


class Provincia(Base):
    __tablename__ = "provincias"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)

    ciudades: Mapped[List["Ciudad"]] = relationship(back_populates="provincia")

    def __repr__(self):
        return f"<Provincia(id={self.id}, nombre={self.nombre})>"


