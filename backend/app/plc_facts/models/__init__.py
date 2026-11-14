"""仅导出本 owner 的 v2 模型；不连接数据库。"""
from .v2 import SampleV2, LatestPointV2
from .source_registry import PlcSourceRegistry
