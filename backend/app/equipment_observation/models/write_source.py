"""观测写入来源登记、稳定内部标识与逻辑删除状态。"""
from sqlalchemy import Boolean, Column, Index, String, text
from sqlalchemy.dialects.mysql import DATETIME, VARCHAR

from database import Base


class WriteSource(Base):
    __tablename__ = "observation_write_sources"

    source_key = Column(VARCHAR(64, charset="utf8mb4", collation="utf8mb4_bin"), primary_key=True)
    storage_identity = Column(VARCHAR(64, charset="utf8mb4", collation="utf8mb4_bin"), nullable=False)
    name = Column(String(128))
    enabled = Column(Boolean, nullable=False, default=True, server_default=text("1"))
    created_at = Column(DATETIME(fsp=6), nullable=False)
    updated_at = Column(DATETIME(fsp=6), nullable=False)
    deleted_at = Column(DATETIME(fsp=6))

    __table_args__ = (Index("uq_obs_write_source_identity", "storage_identity", unique=True),
                      {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"})
