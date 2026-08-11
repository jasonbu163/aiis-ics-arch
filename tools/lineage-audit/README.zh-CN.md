# Lineage Audit

`lineage-audit` 静态盘点前端源文件、后端路由/模型及其证据边。它是离线复核
工具：不调用 API、不读取数据库或 PLC，也不生成业务映射。

## 使用

从 `tools/` 执行：

```bash
uv run python lineage-audit/main.py \
  --frontend-root ../frontend-js/src \
  --backend-root ../backend/app \
  --outputs-dir lineage-audit/outputs
```

仓库中的 `inputs/` 和 `outputs/` 有意保持为空。实际审计请使用私有或临时
fixture 目录；生成的 CSV/JSON/Markdown 证据不得提交到公开基线。
