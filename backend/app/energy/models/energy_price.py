"""能源价格追加快照：精确数值、备注约束与数据库时间。"""
from decimal import Decimal
from sqlalchemy import CheckConstraint, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from database import Base, TimestampMixin


class EnergyPrice(Base, TimestampMixin):
    __tablename__ = "energy_prices"
    __table_args__ = (
        *(CheckConstraint(f"{name} >= 0 AND {name} <= 999999.9999", name=f"ck_energy_prices_{name}_range")
          for name in ("electric_price", "hydrogen_price", "argon_price")),
        *(CheckConstraint(f"char_length({name}) <= {limit}", name=f"ck_energy_prices_{name}_length")
          for name, limit in (("electric_remark", 500), ("hydrogen_remark", 500), ("argon_remark", 500), ("remark", 2000))),
        Index("ix_energy_prices_created_at_id", "created_at", "id"),
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
