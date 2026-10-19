# 本地采集夹具

DAA-002 脱敏确定性输入，不是现场配置或真实 PLC 事实。

- `flat.db` / `offsets.json`：9 个 BOOL 后接 BYTE/INT/REAL。独立预期偏移为 0.0–1.0、byte 2、INT 4、REAL 6，DB 偶数末端 10；不递归猜布局。
- `nested.db` / `nested.udt`：完整 ARRAY[-1..1] OF UDT 和 ASCII STRING，展开 7 个默认禁用/未分组叶点，地址须人工确认。
- `invalid.db`：真实文件/行/路径的多维数组拒绝。
- `transport.json`：两个冻结内存端点/DB 字节，含超过三位小数的 REAL；不打开网络。仅 debug 验证或 cfg(test) 编入此适配器。真实 Snap7 测试另行拥有回环 socket/server。
- `empty.env`：显式 local/read 门禁，旧 DB/写入/授权/autostart 关闭。只复制到新拥有的 canonical 系统 tmp 验证 profile，不覆盖真实 env。

profile marker `.daa-local-validation-owner` 内容须精确为 `DAA-002-r2-owned\n`，显式绝对 env/profile/fixture，拒绝 symlink 祖先和继承 DAA 覆盖。冻结 `failAt` 仅命名激活/提交断点；`cycle_hot_journal` 刷出产品实际事务 page cache、输出 marker，最多等待 10 秒，由自有 controller 发 SIGKILL；无任意 SQL。产品无 ACK 夹具命令，ACK 种子仅 Rust cfg(test)。

偏移依据：[Siemens S7-300 集成示例 §5.3 p34](https://support.industry.siemens.com/cs/attachments/50708061/50708061_application_pcs7_s7300_en.pdf)说明标准 DB 的 BOOL 打包、BYTE/CHAR 下一字节、其余 WORD 边界，并给独立 BOOL/BYTE/BOOL 例子；[TIA 标准 DB 原理](https://docs.tia.siemens.cloud/r/en-us/v21/programming-data-blocks/basic-principles-for-programming-of-data-blocks)说明 DB 末端填充到 WORD。只支撑上述标准平铺子集，不推及优化/复杂布局，也不代替另批 TIA/现场校核。
