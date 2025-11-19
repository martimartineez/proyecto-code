from sqlalchemy import Column, Integer, Text, CheckConstraint, ForeignKey, DateTime, func, String
from sqlalchemy.orm import relationship
from src.core.database import Base

class Reseña(Base):
    __tablename__ = "resenas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    texto = Column(Text, nullable=False)
    puntaje = Column(Integer, nullable=False)

    inserted_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False) # cambiar Usuario por UsuarioPublico
    id_sitio = Column(Integer, ForeignKey("sitios_historicos.id"), nullable=False)

    usuario = relationship("Usuario", backref="resenas") # cambiar Usuario por UsuarioPublico
    sitio = relationship("SitioHistorico", backref="resenas")

    __table_args__ = (
        CheckConstraint('puntaje >= 1 AND puntaje <= 5', name='check_puntaje_range'),

        CheckConstraint("length(texto) >= 20", name="check_text_length"),
        CheckConstraint(
            "estado IN ('pendiente', 'aprobada', 'rechazada')",
            name="check_estado_valido"
        ),
    )

    estado = Column(
        String(20),
        nullable=False,
        server_default="pendiente",
    )

    motivo = Column(Text, nullable=True)
    def to_dict(self):
        return {
            "id": self.id,
            "site_id": self.id_sitio,
            "rating": self.puntaje,
            "comment": self.texto,
            "inserted_at": self.inserted_at.isoformat() + "Z" if self.inserted_at else None,
            "updated_at": self.updated_at.isoformat() + "Z" if self.updated_at else None
        }