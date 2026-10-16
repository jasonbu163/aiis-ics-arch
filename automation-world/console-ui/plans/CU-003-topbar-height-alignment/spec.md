Task ID: CU-003
Revision: r1
Status: owner_approved
Owner Role: BACKFILL Recorder
Allowed Writers: Codex, Human Owner
Handoff: Human Owner 于 2026-10-16 验收 CU-003 r1；事后范围记录已确认
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: CU 顶栏状态胶囊与主题、语言控件高度对齐
Owner: Console UI
Acceptance Chain Reference: CU-003 r1 / BACKFILL 实施与自检 -> Human Owner 人工确认
Related Task: CU-002（保留其 r1 历史验证，不继承最终验收）
Workflow Mode: BACKFILL
Record Timing: post-implementation
Actual Recorder: Codex /root

# CU-003：顶栏三个控件高度对齐

2026-10-16（Asia/Shanghai），Human Owner 指出截图中的三个控件高度不一致，并要求：

> 这个三个组件的高度是不是不一致？请直接调整然后回填3md即可。我人工再次确认后在决定是否接受。

本请求明确选择 BACKFILL。本文件在代码调整和自检之后创建，不倒填事前 PM/spec 批准；本次未调用命名 PM、Development 或独立 Verification。起草时最终接受待定；Human Owner 于 2026-10-16 明确验收 CU-003 r1，当前 owner_approved 记录事后确认，不表示发生过 STD 事前批准。

## 实际范围与验收

- R1：顶栏的 Design sample 状态胶囊、ThemeToggle、LanguageSwitch 统一为 44px，并保持上下边缘对齐。
- R2：只修改 `src/ui/styles/components.css`，新增 `.aw-ui .topbar-actions > .status-capsule { height: 44px; }`。其他位置状态胶囊、两个切换组件 API、顶栏整体布局和其他 Agent 不变。
- AC1：运行预览中三个控件的实际高度均为 44px，top/bottom 一致。
- AC2：相对本次起点，源码只增加上述一行规则；原有状态胶囊默认样式保留。
- AC3：CU `pnpm build` 成功；仅做本次高度的聚焦检查，不做全量回归。
- Human Owner 最终接受：2026-10-16 已明确接受 CU-003 r1，详见 checklist 的原话记录。

本次文档范围是本目录三个事后记录文件及 CU PLAN/catalog 双语索引。CU-002 的历史三文件保留；本修正不冒充其 r1 已重新通过独立 QA。

## 风险与恢复

规则仅作用于顶栏直接子级的状态胶囊，不改变公共组件默认尺寸或行为。需要恢复时，核对当前改动归属后只移除本次新增规则，不覆盖此前 CU-001/CU-002 工作树。无依赖、文案、Rust、端口、数据库或设备修改。

实际实施与命令见 [tasks](tasks.md)，同一实施者的自检及人工确认状态见 [checklist](checklist.md)。
