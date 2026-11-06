# 阶段 C 事实投递手册

[English](STAGE_C_GUIDE.md)

DAA-008 r1 当前为 A-only 源码候选。[Development 记录](plans/DAA-008-reliable-facts-upload/tasks.md)保存实际检查与 hot-journal 恢复阻碍。A0/A1 尚未全通过，实际 HTTP/DS/MySQL、原生视觉与完整阶段 C 验收均待后续批准。以下运行步骤必须等具体 B 环境另批后才执行。

## 开始条件与责任

- 保留所有已有 profile、配置及历史。旧 config-v2/runtime-v2 继续本地能力，本版不迁移、不上传旧历史。
- B 必须明确全新空绝对 profile、后端候选/origin/target ID、专用 MySQL schema/revision/时区、PLC 准入与 source binding、受控 DS 实例、故障及资源收尾。本手册不指定目标，不授权部署。
- 后端责任方按自身获批流程采用 schema/时间/source。DAA 不持有 MySQL/HMAC 凭据，也不能执行采用。匿名来源声明只是准入材料，不是认证。
- B 批准后沿用普通 `pnpm tauri dev`。启动时连接、采集、上传均为停止。debug fixture 宿主不能使用事实 HTTP adapter。

新空 profile 建 config SQLite v2/runtime SQLite v3；样本/manifest 仍 v2，context 仍 v1。未知组合、缺库、WAL、身份/时间/schema 不符或 symlink 均拒绝。r1 对真实 hot rollback journal 目前也会拒绝：不要删 journal、改低版本或强用旧程序打开 v3。保留完整新 profile 并报告错误；恢复协议需 r2 批准。

## 一次配置与显式操作

1. 用获批新 profile 启动，核对停止态。沿用已接受的最小 PLC/采集组配置；激活、连接、采集分别操作。导入或保存不启动 I/O。
2. 先本地保存至少一轮完整样本，在上报与存储页打开“查看接入材料”。向后端责任方交付精确 instance/PLC/generation、context SHA、定义集摘要和序号窗口。生成材料不发 HTTP。
3. 后端明确完成采用后，打开“上报设置”，填已核 target ID、origin 与采用引用，只勾选已核 PLC 并填其十进制字符串序号窗口及引用。周期默认 5 秒，可选 1–3600 秒；合同摘要固定只读。独立 CAS 保存，不产生采集配置版本。
4. 对已有 PLC 使用“读取测试（GET）”，默认 latest limit=1，只检验读取准入。latest/history 没有某事实，不能证明旧 POST 未提交。
5. 加载本地历史后查看原轮只读包预览。请求只从同轮已提交原 payload/manifest/context 生成，没有 JSON 编辑器或第二套上传点开关。
6. 在工作台分别显式开始采集和上传，二者独立控制。上传一次只有一个 HTTP，保留冻结身份，在 PLC/组间按持久 3:1 最新/历史机会轮转，最多八个未终结冻结批。
7. 以“可靠确认”数增长核对本地结果，不以发送次数代替。投递详情展示不可变摘要/成员/父关联及原回执。只有全固定片均有有效证明且同 runtime ACK 事务提交后，样本才已确认；原采集质量与回执当时完整性分开。

## 人工读取核对

读取弹窗提供 latest（每页 8 点）、明确从最早现存基线开始的 changes（每页 8 项）、固定上海时间范围的 projection（每页 8 项）与 original（每页 1 项）。范围为左闭右开，按 `Asia/Shanghai` 输入。界面显示到秒，原 wire 字符串保留精度。

每次明确操作只读一页，最多 2 MiB。“继续”保留 opaque cursor 与筛选；达到 20 页后提示未完成，必须明确开启新预算继续。空页、`scanBudgetReached` 不等于完成；gap、cursor 过窗或不匹配显示核对未完成，需明确重选固定范围或最早基线。不会悄然跳 tail，也不保存 SMA checkpoint。核对只写 `read_result` 诊断，绝不确认 batch。原响应 JSON 不重造数字词法。

两处投递卡按不重复的本地样本计数：待确认总数＝待冻结＋已冻结待确认＋需处理，同一样本多片或多批不会增加样本数。已冻结包含已准备、发送中、重试和结果未知；阻塞、过期未确认及人工复核归需处理，可靠确认另列。

投递队列、上传事件和采集日志分别查看。列表默认 20 条，可选 10/20/50，有界 cursor 分页。列宽按稳定字段保存本机偏好，可恢复默认，不更改业务配置。

## 失败停在哪里

- 超时、坏 UTF-8/JSON、截断、错误媒体类型、成员/摘要不符、ACK 本地落盘失败，均保留原冻结请求为 unknown。继续时重发相同目标、ID、创建时间、摘要及字节。GET 永不替代 ACK。
- 只有严格有效的可靠终结拒绝，才允许原成员合法子集带父 token 派生，父链最多八层；unknown 父不能退休。token、点值和 body 不写日志。
- 原值按 provider 的自然月规则到期；保留证明可确认历史提交并明确 `valueReadable=false`。证明/token 到期进入复核，不改时间、换身份或删除待传样本。
- 真实未决请求存在时，拒绝变更目标/origin/合同/source 声明。只有从未冻结的来源待采用诊断，才可在匹配的 CAS 材料更新后重评估。同 URL 被静默换库不能依靠不存在的 epoch/adoption 字段自动识别。
- 物理预算包含 SQLite/journal、请求、回执、元数据及额外 32 MiB ACK 恢复预留。高水停止新采样/新冻结并保留恢复机会；真实 I/O 故障仍可能 unknown。pending、blocked、unknown 及有引用材料不因保留期删除。
- 暂停禁止新派发，在途请求按有界时限收尾并持久有效结果。正常退出保留未决身份；重开不自启采集/上传。r1 的 hot-journal 缺口仍是其崩溃恢复主张的明确阻碍。

## 后续 B 证据

另批后只做必要增量：受控值 → 本地原文/SHA → POST/回执 → 本地 ACK → latest/history；暂时断开 API 后恢复；正常退出并重开，不点启动即核停止态，再显式继续。保留双方身份/值/quality/时间/摘要账。无需重做阶段 B 整套导入、命名和分组。

遇存储/schema/时间/source 冲突、证明过期或 unknown，停止并保留新 profile。向后端责任方交接目标/source/读取诊断，向 Development 交接 batch/receipt ID 与摘要，不附凭据或父 token。原生视觉、实际 HTTP、DS/MySQL/Docker 与资源清理均按精确 B 方案执行；A-only 检查和构建成功不证明端到端或生产可用。
