from src.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column

class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    status: Mapped[str] = mapped_column()

    def __repr__(self):
        return f"Issue(id={self.id}, title={self.title}, status={self.status})"