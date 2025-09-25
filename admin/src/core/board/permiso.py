from src.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class Permiso(Base):
    __tablename__ = 'permisos'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    def __repr__(self):
        return f"<Permiso(id={self.id}, nombre={self.nombre})>"