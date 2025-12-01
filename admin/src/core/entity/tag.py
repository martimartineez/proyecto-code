from __future__ import annotations
from typing import List, TYPE_CHECKING
from datetime import datetime, timezone
from sqlalchemy import (
    String,
    Integer,
    Table,
    Column,
    ForeignKey,
    Date,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base

if TYPE_CHECKING:
    from src.core.entity.sitio_historico import SitioHistorico


tags_sitios = Table(
    "tags_sitios",
    Base.metadata,
    Column("idTag", ForeignKey("tags.id"), primary_key=True),
    Column("idSitio", ForeignKey("sitios_historicos.id"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)

    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)

    baja: Mapped[bool] = mapped_column(Boolean, default=False)

    sitios: Mapped[List["SitioHistorico"]] = relationship(
        secondary=tags_sitios,
        back_populates="tags",
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
        return f"<Tag(id={self.id}, nombre={self.nombre})>"
