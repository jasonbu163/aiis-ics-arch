# 使用手册原生图片来源

[English](README.md) · [使用手册](../../../USER_GUIDE.zh-CN.md)

这7张PNG由主协调于2026-10-22在真实原生窗口取得，合成profile，无图片生成、像素编辑或浏览器预览替代。仅拷贝原图字节。

| 文件 | UTC取图时间 | 步骤 | SHA256 |
| --- | --- | --- | --- |
| [01-workbench.png](01-workbench.png) | 2026-10-22T06:14:34.593Z | 首次启动：空配置、停止、连接为0 | `aefadea6f73cd36f6c068145ab94c9bbb2d98278aacf37bfe5fc171f2ecf34c2` |
| [02-instance-editor.png](02-instance-editor.png) | 2026-10-22T06:17:58.386Z | 配置中心/实例：PLC_Test，127.0.0.1:30102，Rack0 Slot1，TSAP256，16/4 | `628b7183167cf2f87c437dc51df1d73eb631ca8386fcdd4723bbf3e424e77541` |
| [03-manual-point.png](03-manual-point.png) | 2026-10-22T06:18:32.457Z | 手工BOOL：Run_Bool，byte0 bit0，填写人工地址理由 | `63bf9b456a6e4105ea30c8876a4f919abf3b38793dd7dfa0a36409ab66c543ca` |
| [04-manual-layout.png](04-manual-layout.png) | 2026-10-22T06:20:06.486Z | 完整人工地址预览：布局校验通过，地址需在主表核对 | `0b3f8d840c37ccebc55e8c3aa9a768e8c69372e48636779e021a0164890e20f9` |
| [05-policy.png](05-policy.png) | 2026-10-22T06:24:17.127Z | 当前可执行示例：REAL斜坡0..100，周期10000ms，显式初值0；非零初值输入回退另记已知问题 | `eddd0d86f43af59db075e5dc1c0122ee5c287e61269a1f918780b860d2a0216f` |
| [06-apply-preview.png](06-apply-preview.png) | 2026-10-22T06:25:07.998Z | 选择最新保存序号7，停机加载三点，核对恢复初值清单并勾选确认 | `def4ad4418763b429245e92bf19a44f2df70765258d334bf0a1aa4ddbfbf5abf` |
| [07-online-values.png](07-online-values.png) | 2026-10-22T06:26:57.569Z | 三手工点运行：BOOL翻转、REAL斜坡、Setpoint_Int普通写入12；表格左侧名称地址与值 | `9012c04035ca263633da61b1b4bdbdf7d40f613b16dcabc2f0a314055ad84651` |

## 事实和未完成步骤

DB名为Manual_Demo，DB31长度8，三点BOOL0.0/INT2/REAL4。BOOL半周期1500ms（通用period保留1000），REAL斜坡0..100/10000ms，初值false/0/0。主协调观察到普通写12、BOOL两态、REAL变化及暂停/恢复/停止。单张图不证明翻转。

非零初值20真实键入回0；持续fixed值仅为同绑定的源码风险，未独立动态复现。05旧尝试在raw另存，正式05是初值0的重拍；07以最后左侧列图为准。旧截图意图文字不等于输入已生效。既有自动化input/change同步事件不替代真实键入证据。

最新Owner要求自行操作反馈，覆盖附录B机械10图要求。导入绑定/导入命名/停止态重开三步无图，不建立08/09/10文件或图片引用；完整文字步骤保留。重置、导入提交、正常退出/重开未完成，不给出已走通结论。

## 原件与保留资源
原件档案: `/Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r5-evidence/dev-run-0331`; inventory SHA256 `e53f29e7c4e3c5bdf39040fa2645f73c8adabb46744b67aa84fb30121b75c3e0`. 逐成员SHA见inventory.json；原始观察、取图尝试、样例副本SHA和来源在raw及launch.json，不改既有QA封存。

源候选 `306a09d5317931482a59f45da5eafcb9d3ee739199799f475ade1891fb0b00b4`; 原QA productDesktop SHA256 `a6b485e86232151f021d076a3f8acdf48b98decfc4af9217058a3a7969dae11d`. 同字节载体native库SHA256 `83ab0462ba83c536d9d8eda93b8a57005802ab734a2229b53f101023a7b41ad5`.

主协调最初后台启动PID88101未取得成功退出码，sandbox前台尝试exit134，均不算正常退出。后续原生载体PID89100/session90871仍运行，Owner已接管Open文件选择器；未选文件。profile为T5/profile/dev/user-guide-20261022，载体为T5/tmp/dev/user-guide-20261022/DS-User-Guide-Capture.app（T5=/private/tmp/arch-aw-005-r5-exec）。保留供用户操作，不关闭或清理。30102 lsof exit1空仅是该时点无listener，非进程退出证明。Owner完成并释放示例后，再确认自有进程/listener释放才回收载体；不删除未知资源。
