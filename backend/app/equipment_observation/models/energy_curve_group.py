"""能耗曲线组持久模型，配置与观测样本独立。"""
from sqlalchemy import BigInteger, Boolean, Column, Index, JSON, String
from sqlalchemy.dialects.mysql import VARCHAR

from database import Base


class EnergyCurveGroup(Base):
    __tablename__ = "energy_curve_group_configs"

    curve_group_key = Column(VARCHAR(64, charset="utf8mb4", collation="utf8mb4_bin"), primary_key=True)
    title_zh = Column(String(128), nullable=False)
    title_en = Column(String(128), nullable=False)
    meter_id = Column(VARCHAR(64, charset="utf8mb4", collation="utf8mb4_bin"), nullable=False)
    group_key = Column(VARCHAR(64, charset="utf8mb4", collation="utf8mb4_bin"), nullable=False)
    sort_order = Column(BigInteger, nullable=False)
    enabled = Column(Boolean, nullable=False)
    series = Column(JSON, nullable=False)

    __table_args__ = (
        Index("ix_energy_curve_groups_meter", "meter_id"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )
