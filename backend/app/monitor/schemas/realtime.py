"""Monitor Core latest snapshot response helpers."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class LatestSnapshotResponse(BaseModel):
    """项目无关的 latest 事实摘要；业务字段保留在 decoded_payload。"""

    model_config = ConfigDict(extra="allow")

    device_id: int
    snapshots: list[dict[str, Any]]
