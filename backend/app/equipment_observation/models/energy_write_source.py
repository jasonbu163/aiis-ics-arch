"""能耗写入来源登记、稳定内部标识与逻辑删除状态。"""
from sqlalchemy import Boolean, Column, String, UniqueConstraint, text
from sqlalchemy.dialects.mysql import DATETIME, VARCHAR

from database import Base


class EnergyWriteSource(Base):
    __tablename__ = "energy_write_sources"

    source_key = Column(VARCHAR(64, charset="utf8mb4", collation="utf8mb4_bin"), primary_key=True)
    storage_identity = Column(VARCHAR(64, charset="utf8mb4", collation="utf8mb4_bin"), nullable=False)
    name = Column(String(128))
    enabled = Column(Boolean, nullable=False, default=True, server_default=text("1"))
    created_at = Column(DATETIME(fsp=6), nullable=False)
    updated_at = Column(DATETIME(fsp=6), nullable=False)
    deleted_at = Column(DATETIME(fsp=6))

    __table_args__ = (UniqueConstraint("storage_identity", name="uq_energy_write_source_identity"),
                      {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"})
