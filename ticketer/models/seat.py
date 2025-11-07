"""Seat model."""

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ticketer.db.base import Base


class Seat(Base):
    """Seat model for seat-level ticketing."""

    __tablename__ = "seats"
    __table_args__ = (
        UniqueConstraint("event_id", "seat_label", name="uq_event_seat"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)
    seat_label: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "A1", "B5"
    row: Mapped[str] = mapped_column(String(10), nullable=False)
    col: Mapped[int] = mapped_column(Integer, nullable=False)
    is_reserved: Mapped[bool] = mapped_column(default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<Seat(id={self.id}, event_id={self.event_id}, label={self.seat_label})>"

