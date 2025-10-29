from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import BigInteger, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from src.core.database import Base


class HistorialSitio(Base):
    __tablename__ = "historial_sitios"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    idSitio: Mapped[int] = mapped_column(
        Integer, ForeignKey("sitios_historicos.id"), nullable=False
    )
    idUsuario: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=False
    )

    accion: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # CREATED | UPDATED | DELETED
    fechaAccion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    valoresAnteriores: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    valoresNuevos: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<HistorialSitio(id={self.id}, idSitio={self.idSitio}, idUsuario={self.idUsuario}, "
            f"accion={self.accion}, fechaAccion={self.fechaAccion})>"
        )
