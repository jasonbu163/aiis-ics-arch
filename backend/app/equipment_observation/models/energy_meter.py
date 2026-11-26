"""能耗表计的持久名称与登录角色可读范围。"""
from sqlalchemy import Column, JSON, String
from sqlalchemy.dialects.mysql import DATETIME, VARCHAR

from database import Base


class EnergyMeter(Base):
    __tablename__ = "energy_meters"

    meter_id = Column(VARCHAR(64, charset="utf8mb4", collation="utf8mb4_bin"), primary_key=True)
    name_zh = Column(String(128), nullable=False)
    name_en = Column(String(128), nullable=False)
    read_roles = Column(JSON, nullable=False)
    created_at = Column(DATETIME(fsp=6), nullable=False)
    updated_at = Column(DATETIME(fsp=6), nullable=False)

    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}
