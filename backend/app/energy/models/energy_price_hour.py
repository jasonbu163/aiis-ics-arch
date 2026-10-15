"""能源小时快照：UTC 事件时间、唯一小时键与数据库 UTC 修改时间。"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint, DateTime, Index, Integer, Numeric, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.mysql import DATETIME
from database import Base


class EnergyPriceHour(Base):
    __tablename__ = "energy_price_hours"
    __table_args__ = (
        *(CheckConstraint(f"{name} >= 0 AND {name} <= 999999.9999", name=f"ck_energy_price_hours_{name}_range")
          for name in ("electric_price", "hydrogen_price", "argon_price")),
        *(CheckConstraint(f"char_length({name}) <= {limit}", name=f"ck_energy_price_hours_{name}_length")
          for name, limit in (("electric_remark", 500), ("hydrogen_remark", 500), ("argon_remark", 500), ("remark", 2000))),
        UniqueConstraint("hour_start", name="uq_energy_price_hours_hour_start"),
        Index("ix_energy_price_hours_observed_at_id", "observed_at", "id"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    electric_price: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    hydrogen_price: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    argon_price: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    electric_remark: Mapped[str | None] = mapped_column(Text)
    hydrogen_remark: Mapped[str | None] = mapped_column(Text)
    argon_remark: Mapped[str | None] = mapped_column(Text)
    remark: Mapped[str | None] = mapped_column(Text)
    operator: Mapped[str] = mapped_column(String(50), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime().with_variant(DATETIME(fsp=6), "mysql"), nullable=False)
    hour_start: Mapped[datetime] = mapped_column(DateTime().with_variant(DATETIME(fsp=6), "mysql"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime().with_variant(DATETIME(fsp=6), "mysql"), server_default=text("(UTC_TIMESTAMP(6))"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime().with_variant(DATETIME(fsp=6), "mysql"), server_default=text("(UTC_TIMESTAMP(6))"), nullable=False)
