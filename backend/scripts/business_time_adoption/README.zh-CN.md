# 业务时间采用证据

English: [README.md](README.md)。

本工具仅调查 BE010 固定13表41列、准备候选计划及比较只读快照。不执行schema/data变更、不从时间数值推断时区、不启动writer、不安装采用文件或授予采用批准。未知、混合且无法分类的来源继续阻止G-T解除。

裸入口只显示help，不加载配置、dotenv、模块或目标：

```bash
cd backend
uv run --offline --frozen --no-sync python scripts/business_time_adoption/main.py
```

具体目标操作须另获批准。将 `.env.example` 复制到目标受控私有位置并显式指定**绝对**路径。专用process `BUSINESS_TIME_DB_*` 优先于显式文件，不回退读取工具或backend真实 `.env`。只有显式工具engine使用目标配置。账号仅需固定列、UUID/schema/时钟、information_schema和current revision探针的只读资格。报告保存计数、metadata和按主键排序的逐列摘要，不保存行原文、密码或DSN。

```text
... main.py inspect --module equipment --env-file /private/approved/tool.env --source-revision <已审阅源码> --output /private/approved/inspection.json
... main.py plan --module equipment --inspection-report /private/approved/inspection.json --classification-report /private/approved/classification.json --source-revision <已审阅源码> --output /private/approved/plan.json
... main.py verify --module equipment --env-file /private/approved/tool.env --inspection-report /private/approved/inspection.json --source-revision <已审阅源码> --output /private/approved/verification.json
```

`plan`离线运行。`business-time-classification/v1`须精确覆盖调查的每个`table.column`，记录basis（utc_wall/shanghai_wall/known_offset/unknown）、与调查相等的coveredRows和指向私有来源证据的evidenceRef。这些声明不能自动变成历史证明；计划始终为state=candidate、adoptionEligible=false。`verify`比较同一目标/profile、行数和时间列摘要；摘要变化不证明转换正确，也不替代ID/值/FK/pair守恒。旧HTTP/Projection兼容、writer隔离、备份、明确获批的data-only转换及Owner目标采用决定仍须独立证明。

运行凭据 `business-time-adoption/v1` 是另一份运维工件：精确 module/profile/schemaRevision（`1b3d5f7a9c20`、`2c4e6a8b0d12`、`3d5f7a9c1e23` 或 `4e6a8b0d2f14`，必须匹配实际数据库）、目标UUID/schema、固定列摘要、sourceRevision、完整be010.fixed-basis/v1、调查/转换/校验报告digest/reference、备份和Owner批准引用、上海verifiedAt及state=adopted。工具不把candidate提升为该凭据。外部私有材料由部署方保护，原子替换须保留旧摘要，不进入公开仓。

终端输出JSON Lines started/complete/failed，报告仅写入显式指定的新文件，不覆盖已有文件。不默认创建inputs/outputs、持久日志、打包工件或独立可执行文件。使用项目uv环境，独立打包不在本任务范围。源码检查不授权任何目标操作。
