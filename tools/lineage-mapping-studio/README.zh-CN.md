# Lineage Mapping Studio

这是一个本地 Vue 工具，用于可视化 `lineage-audit` 生成的 lineage 证据。它
只是复核界面，不是运行时配置编辑器，也不是数据源真相库。

仓库中的 `inputs/` 和 `outputs/` 保持为空。实际复核时从私有或临时工作区导入
已审核的证据包，复核完成后丢弃生成包。

```bash
pnpm install
pnpm build
```
