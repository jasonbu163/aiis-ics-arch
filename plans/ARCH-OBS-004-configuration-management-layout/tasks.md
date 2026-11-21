Task ID: ARCH-OBS-004
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development, Human Owner
Handoff: 隔离候选及自检已完成，交协调者进行正式整合及 fresh-context Verification
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Acceptance Chain Reference: [已批准 r1](spec.md) → 本记录 → 独立验证 → Human Owner 最终验收

# 设备状态与过程监控配置管理调整 r1 实施记录

## 实施与自检

- 槽位目标和采样组可独立省略，只有精确分区返回原剩余容量。表计全量查询在既有角色表计范围内条件化，显式传入具体表计仍走原检查，标准响应保持原形状。
- 两页上卡使用公共配置分类选择，下卡分别显示标题与操作、筛选、对应表格。筛选按提交生效，重置当前表条件，切换保留已提交项。覆盖跨目标／组、跨表计身份、首次使用时间和列宽；表计新增从可访问表计明确选择，编辑用行的完整身份。保持能耗样本管理逻辑。
- 更新两份操作手册和成对 i18n。仅修改已有文件，未改变源码结构或数据库模式。

| 检查 | 执行及结果 |
| --- | --- |
| 后端 HTTP | 在隔离候选 backend 使用仓库已锁定虚拟环境，`UV_NO_CACHE=1 UV_PROJECT_ENVIRONMENT=<既有虚拟环境> uv run --no-sync --offline python -m pytest -q -p no:cacheprovider tests/test_equipment_observation_r10_flow.py`，22 passed。通过独占内存 SQLite、ASGI 模拟 HTTP 检查全部／部分／精确参数、停用、首次使用时间、真实数据作用域语义、无权限与旧接口。未连接真实数据库。 |
| 前端模块和组件交互 | 在隔离候选 frontend-js 使用锁定依赖，`VITE_SUPERVISOR_PAGE_ACCESS_JSON='[]' VITE_OPERATOR_PAGE_ACCESS_JSON='[]' pnpm --config.verify-deps-before-run=false run test:modules`，93 passed。覆盖两类全量、重置、关键词、乱序隔离及原样本行为。 |
| 前端生产构建 | 在同一候选以相同的两个角色环境变量和 `VITE_API_BASE_URL=/api/v1` 执行 `pnpm --config.verify-deps-before-run=false run build`，成功。Vite 有既有大依赖包大小提示。 |
| 浏览器交互预检 | 协调者用候选 `browser-smoke.cjs` 与隔离 Chrome 执行两条真实页面路由，合成且完全拦截 HTTP。布局、默认全量、英文关键词、组筛选、重置及 meterB 精确编辑通过。开发沙箱原生回环监听 EPERM，因此使用隔离浏览器路由拦截。此项是额外自检，不代替独立 Verification。 |
| 文档与差异 | 配对操作手册本地链接、双语 locale 顶层业务键对称、修改文件新增尾随空白检查通过。14 个文件经正式树当前字节基线比对，`git apply --check` 通过。 |

候选由当前未提交正式源码工作树复制，基准 HEAD 为 `cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81`，逐文件基线包含当时已有并行修改。隔离目录为 `/private/tmp/arch-obs-004-candidate.BnilRdCD`，复制过程排除真实环境文件、用户数据、日志、原有构建和运行配置。候选仅包含公开 `.env.example` 衍生的隔离测试设置。正式候选统一差异为 `r1-candidate.patch`，SHA-256 `5bd115b117456cbfea940eadd2d81b4ae4ba618107b3034d2b9e462c62542323`，批准 spec SHA-256 `d7aeb782a7b578f62d200da4aebeacb412d43c3bea58072768c58ab1f8978971`。补丁由下表 14 个文件生成。

| 文件 | 正式基线 SHA-256 | 候选 SHA-256 |
| --- | --- | --- |
| `backend/app/equipment_observation/api/routes.py` | `6c0d275a08516a3487b6926cd1e63649247036b95e04a14bb59f9016b9142786` | `3d50f4480b3ec4a167001a5fcde7c5a88b5e8aebd7f4aa2499964cd2fc6ce649` |
| `backend/app/equipment_observation/services/configuration.py` | `aa3ab6a53fcfa0cc30529a6cebd6e9c09fe1857693bcc5857a5cc35b6e31aa49` | `ebb23a84b43ab44f0cdc9bb75a73b459c8a54eb0b1d513b4bdb57ed032d213d5` |
| `backend/tests/test_equipment_observation_r10_flow.py` | `340aabc97f9a59f09a930a49ef7d2e56a2e296c3584165e7db58017069790446` | `31b8cc740bc3c8f7fc255ec3cf51a43e19d2ff7242240c1837277ce75bfb60f4` |
| `docs/equipment-status-process-monitoring-guide.md` | `1bfcdc33a2e1b5dd8e75d03a9bf8426260020fb1d5d3370c997830eaeded303e` | `d202111ee14eb84f0af5aff60a451959416209f21f251759baa0ea17d4954858` |
| `docs/equipment-status-process-monitoring-guide.zh-CN.md` | `f73f14a1b6a56fdb40452e865545d868ca0d7add0e16f5ac06d78b86ff9a33cf` | `5bc7bf31420c1e0c1dc0b4442dad0736349e8974eaeac490291618ddc8cd70ea` |
| `frontend-js/src/app/equipment/locales/en-US.json` | `d92fa87ca95b79f6e937b7cb6a93f9ec3774fd5f2004cfc1ffe09a58f300c802` | `0c4448870bb4591c269730390b554cf03da62eb675ec9c04cc64001095b54d61` |
| `frontend-js/src/app/equipment/locales/zh-CN.json` | `a5e63623a9edb7ab43bcf0cbdf02f1626c0a5caaf320e764f2ee33ba43fc0122` | `0b27765f55f0ede2ab798429d25ab2ff6b556d17eacb39ed3744dd87b498b0f9` |
| `frontend-js/src/app/equipment/views/observations/admin.vue` | `dd5c965bf83ce900c52bbb341ad7c249f13d650d1db12893ccfd36173a28dd68` | `91c3b317ae37e24114bde242cca327028da9f2dd0f2934a4a5eab249419b3a10` |
| `frontend-js/src/app/monitor/api/observations.js` | `144992b29bc569d33a9260928cfc49cf6f318c44d09aff8ce9eaf12867c57dc5` | `cd8169d6b5a3bb4aee72974704410ead5337c9bb1ff45b02047362647ad1e987` |
| `frontend-js/src/app/monitor/components/observations/EnergyAdmin.vue` | `7e11059e9a03496b5f39b247e3e98608aaacae68c0e5fb7853fd0fe28da784e1` | `9c33b39bd2e6b6fea5ff74288935828dbfc58e6c5d0105786bb4dd199ce54a46` |
| `frontend-js/src/app/monitor/locales/en-US.json` | `9da15b04fd88f92cf572fb4c6b70a12c09496a4ddcae36751ad8ca782d3444a6` | `ce008e51efd14287552d41663d1448583a8bdd7c3bb0fdef2f24e92d745e762c` |
| `frontend-js/src/app/monitor/locales/zh-CN.json` | `9429bead0f39e0c97159a2e9f25b601c974746b3b7cd3bee86c08073d7d681ea` | `54a844d7f69c88cb20f0ceca58e971e99415e6712caddce7607f68f0859168b9` |
| `frontend-js/src/app/monitor/views/observations/admin.vue` | `3c8678e8af7379dfba1903316c45b4f413f2c72e35a11369f5c7b2a3dd2a2787` | `266e59834cd7a19682c13491102815d20c346ef684082bfb0d881a456fb140b2` |
| `frontend-js/tests/module-registry/equipment-observation-columns.test.mjs` | `d28979a3b7817f1c54e1191255d9cc9f7028db6753f55fc0af9311e8fd939a59` | `1c1fb713da172a59889567762b99d518a0edf57f0cc534ae396271f79c69290e` |

## 交接边界

正式工作树的前端和 Uvicorn 后端仍在运行并可监视源码。实施候选及合成检查已完成，未落盘正式应用源码或触发热重载。正式整合需先协调运行中的服务影响并重新核对上表基线，随后确认交付源码与候选哈希一致。独立 Verification 针对正式交付源码与验收标准记录 verdict。运行中的 dev 服务未用于开发测试，未执行数据库迁移或写入真实数据。

临时目录内包含本任务候选、基线、构建、锁定依赖的本地拷贝及验证脚本和输出。交付整合及独立验证完成、必要证据写入角色记录后，由协调者核对归属并回收此目录。保留的正式证据为规格、任务记录以及独立验证记录。


## r1 返工 1 · 窄屏配置卡片

[保留第一次独立验证](checklist.md) 的 AC01 未通过证据。返工仅修改下表两个 Vue 页面。展开侧栏后，配置卡片在 390px 视口只剩 130px 宽。原卡片操作区按固有宽度占位，重置列宽按钮右边界达到 x440.19。绝对定位的顶栏随工具换行加高，配置分类也会落在顶栏的点击范围内。通过配置页容器断点适配内边距、标题和操作区换行，并为窄屏多行顶栏分档留出空间。复用 BaseCard 和 Element Plus 控件，周期内不修改共享导航和顶栏。过程监控的表计卡片继承同一页窄屏布局。

| 校验 | 证据 |
| --- | --- |
| 生产构建 | 按上文相同命令重跑，退出 0。 |
| 真实 Chrome | 独占候选合成拦截，无外部或真实服务地址，`node browser-narrow.cjs` 在 390×844 通过，`OBS_BROWSER_WIDTH=480 node browser-narrow.cjs` 和 `OBS_BROWSER_WIDTH=560 node browser-narrow.cjs` 均通过。每个宽度均使用普通点击操作，通过槽位、曲线、表计三个「重置列宽」按钮的边界检查，验证两页默认值、表计分类、筛选、重置和准确编辑。390px 三个按钮 x257..350.45 落在卡片 x248..378；展开状态的过程分类 y379..443，顶栏底 y290；侧栏折叠后撤去额外顶距。480px 卡片起点 y252、顶栏底 y238；560px 卡片起点 y200、顶栏底 y186。 |
| 桌面 Chrome | 1260×900 `node browser-smoke.cjs` 退出 0，沿用上文交互。 |
| 候选一致 | 对正式树 14 个原文件逐个比较基线，`git apply --check` 退出 0。其余 12 个候选源码和文档字节与初次交接一致，后端和状态行为没有改动。 |

正式整合应使用 `r1-rework1.patch`，SHA-256 `c5b692af7786f1fbf756fd00fe4ffecb2fa57b83ec866a295ca5f32774c9335f`。全量候选清单 `rework1-manifest.json`，SHA-256 `66fe758bbc73e445e07b0591508233c4ec200e11ee5dcacb89dd65481f03465b`。以下值替换初次交接的两个候选值，原基线与其余值仍有效。

| 文件 | 返工后候选 SHA-256 |
| --- | --- |
| `frontend-js/src/app/equipment/views/observations/admin.vue` | `0d031e7582dc5f6cb506684c6afe38da298ee2f4e6692f91042fea8b86c34ea9` |
| `frontend-js/src/app/monitor/views/observations/admin.vue` | `6f2dcfffd63fdf04e08bd757d4d861fbb39f1b3b388c2f80f29bea2aa9916e22` |

状态保持开发交接，交协调者正式整合与第二轮独立验证。隔离目录中的首次候选补丁保留为 QA1 失败证据，不用于正式整合。

## 正式源码整合及独立验证交接

Human Owner 已授权直接合入正式工作树并告知 5190、8000 已停止。正式路径为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81`。整合前后均使用 `lsof -nP -iTCP:8000 -iTCP:5190 -sTCP:LISTEN` 核对，未发现监听进程。无启动或重启用户服务的动作。

重新验定返工补丁及清单摘要，核对清单全部 14 个正式基线与候选 SHA-256。由 Development 在正式树依次执行 `git apply --check`、`git apply`、`git apply --reverse --check`，均退出 0。整合后重新逐项核对，正式 14 个文件与返工候选逐字节一致。相关路径的 `git diff --check` 退出 0。源码为未提交工作树交付，保留其他并行修改。未连接数据库、执行迁移或变更真实数据。

正式树已具备与已验证隔离构建相同的任务源码。请协调者启动 fresh-context Verification，核对正式树摘要、真实页面验收及工作树边界，并在独立检查记录写明结论。隔离目录保留供本任务独立验证和协调者收尾，不作为最终源码交付。
