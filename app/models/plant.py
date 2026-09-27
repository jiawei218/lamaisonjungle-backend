from uuid import uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def generate_uuid() -> str:
    return str(uuid4())


class Plant(Base):
    __tablename__ = "plants"

    __table_args__ = (
        CheckConstraint(
            "price >= 0",
            name="ck_plants_price_non_negative",
        ),
        CheckConstraint(
            "water BETWEEN 1 AND 3",
            name="ck_plants_water_range",
        ),
        CheckConstraint(
            "light BETWEEN 1 AND 3",
            name="ck_plants_light_range",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    code: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        unique=True,
        default=generate_uuid,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    is_special_offer: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    price: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    water: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    light: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    cover: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )