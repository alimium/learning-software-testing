"""Venue model."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ticketer.db.base import Base


class Venue(Base):
    """Venue model."""

    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)

    def __repr__(self) -> str:
        return f"<Venue(id={self.id}, name={self.name})>"

