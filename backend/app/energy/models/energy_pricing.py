"""能源单价项目、逐项实际小时价格与旧 HTTP 视图所需的小时元数据。"""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.mysql import DATETIME, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


ITEM_KEY = String(128).with_variant(VARCHAR(128, charset="utf8mb4", collation="utf8mb4_0900_bin"), "mysql")
BUSINESS_DATETIME = DateTime().with_variant(DATETIME(fsp=6), "mysql")


class EnergyPriceItem(Base):
    __tablename__ = "energy_price_items"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    item_key: Mapped[str] = mapped_column(ITEM_KEY, primary_key=True)
    name_zh: Mapped[str | None] = mapped_column(String(128))
    name_en: Mapped[str | None] = mapped_column(String(128))
    unit: Mapped[str] = mapped_column(String(128))
    sort_order: Mapped[int] = mapped_column(BigInteger)
    enabled: Mapped[bool] = mapped_column(Boolean)


class EnergyPriceHourMeta(Base):
    __tablename__ = "energy_price_hour_meta"
    __table_args__ = (
        Index("ix_energy_price_hour_meta_observed_at_id", "observed_at", "id"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    hour_start: Mapped[datetime] = mapped_column(BUSINESS_DATETIME, unique=True)
    remark: Mapped[str | None] = mapped_column(Text)
    observed_at: Mapped[datetime | None] = mapped_column(BUSINESS_DATETIME)
    operator: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime | None] = mapped_column(BUSINESS_DATETIME)
    updated_at: Mapped[datetime | None] = mapped_column(BUSINESS_DATETIME)
    has_builtin: Mapped[bool] = mapped_column(Boolean)


class EnergyPriceItemHour(Base):
    __tablename__ = "energy_price_item_hours"
    __table_args__ = (
        Index("ix_energy_price_item_hours_hour", "hour_start"),
        CheckConstraint("price >= 0", name="ck_energy_price_item_hours_price_nonnegative"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )

    item_key: Mapped[str] = mapped_column(ITEM_KEY, ForeignKey(EnergyPriceItem.item_key), primary_key=True)
    hour_start: Mapped[datetime] = mapped_column(BUSINESS_DATETIME, ForeignKey(EnergyPriceHourMeta.hour_start), primary_key=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    remark: Mapped[str | None] = mapped_column(Text)
    observed_at: Mapped[datetime] = mapped_column(BUSINESS_DATETIME)
    operator: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(BUSINESS_DATETIME)
    updated_at: Mapped[datetime] = mapped_column(BUSINESS_DATETIME)
