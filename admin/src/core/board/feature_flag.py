from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class FeatureFlag(Base):
    __tablename__ = "feature_flags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    nombre: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    valor: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    mensaje: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    ultimaModificacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    idUsuarioModificacion: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=True
    )

    def __repr__(self) -> str:
        return (
            f"<FeatureFlag(id={self.id}, nombre={self.nombre}, valor={self.valor}, "
            f"ultima_modificacion={self.ultimaModificacion}, idUsuarioModificacion={self.idUsuarioModificacion})>"
        )
