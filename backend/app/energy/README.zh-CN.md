# Energy 能源单价

[English version](README.md)

energy 是两个价格表、三条路由及独立读写权限的唯一 owner。本公共模块拥有每小时整组能源价格；客户规则与真实数据归消费项目。[backend PLAN](../../PLAN.zh-CN.md) 索引工作，当前合同归 [ARCH-BE-004 r2](../../../plans/ARCH-BE-004-energy-price-hourly-history/spec.md)；[BE002](../../../plans/ARCH-BE-002-energy-price-api/spec.md) 保持已验收的追加历史基线。

## API 与时间合同

启用 manifest 仍只注册 GET `/energy/current`、GET `/energy`、POST `/energy`，归配置的 prefix。GET 要求 energy-price-read，POST 要求 energy-price-manage，互不授予；页面可见不授予 API 权限，原 admin/supervisor/operator guard 保留。

三价格必填，Decimal/Numeric(10,4)，范围 0..999999.9999，最多四位有效小数。原始 JSON 小数先精确解析，兼容十进制字符串，输出 JSON number，0 有效。电价 CNY/kWh，气价 CNY/Nm³。单项备注最多500，总备注2000，空串归null。操作者取认证username；不隐式DDL、seed或填默认价。

POST 新增可选/null observedAt，API 一次捕获 aware UTC now 用于空值兜底及拒未来。明确输入须为带offset ISO datetime，且可持久化MySQL DATETIME并安全转换上海时间；非法、空串、无时区、未来均422。固定Asia/Shanghai归小时，MySQL唯一键 uq_energy_price_hours_hour_start 配合原子upsert整组覆盖价格、备注、observedAt和actor，保留id/hourStart/createdAt。Service提交/回滚，CRUD不控制事务，新HTTP请求重新取now。不引入请求重放或小时任务。

energy_price_hours 的事件/小时/DB创建修改时间均按UTC DATETIME(6)保存，DB表达式UTC_TIMESTAMP(6)，不改变全局连接时区。四个输出时间字段带上海offset。hourStart代表最终小时快照，不证明分钟级生效；updatedAt是实际修改时刻。

current 按 observed_at<=请求now、observed_at DESC/id DESC选择，无有效记录null，缺日沿用最近价格；补历史不能因updatedAt较新抢占当前价。历史仍返回{items,total,page,pageSize}，默认1/20、size1..100；可选严格单值date=YYYY-MM-DD按上海observedAt自然日过滤，总数是过滤后实际条数，空日/越界页items为空，边界日期安全。按observed_at DESC/id DESC，不制造空小时。页面查询选日page1/size24，卡片只读，新增弹窗picker按上海解释、null表示服务端now，同小时覆盖整组；成功切响应记录日并刷新两GET，不把历史POST响应直接赋给current。

业务小时身份为上海民用日期+小时，夏令时回拨重复小时统一fold=0（最早瞬间）生成UTC hour_start，observed_at保留真实事件瞬间，因此每日仍最多24行。picker不存在的民用时间校验失败。wire统一+08:00保留真实瞬间并兼容浏览器，显示和picker解析仍使用IANA Asia/Shanghai历史规则。

## 显式schema与旧数据归并gate

十四表root d4e6f8a0b2c4 和BE002 a6c8e0f2b4d6原样保留；BE004后继b8d0f2a4c6e8创建小时表，形成受保护十六表基线；BE005后继d2f4a6b8c0e2只增42个其他业务表，本任务F组合共58表。energy_prices全部原行及Model保留，Registry/启动/普通请求不归并。

运行采用前独立批准精确源/目标库、原无offset时间来源、已验证可恢复备份、暂停全部新旧写入窗口、命令和回退责任人。不得猜旧时区；确认MySQL Asia/Shanghai命名时区表、服务端与DB时钟。混合/歧义时间或非法转换先解决。预检输出原行数、小时组数、冲突组数、异常数、每小时所选旧id受控本地清单；目标非空或时间不明立即停止，不能覆盖。以下SQL在预检与事务之间要求人工核对，不是无人值守脚本。

同小时按(created_at DESC, id DESC)选最后完整快照，整组复制价格/备注/actor，原created/updated含义经时区转换保留；新id独立。导入后对照旧id清单核对每组值/时间及小时数，原表行数/校验和必须不变，核对后commit再切应用。新表未导入返回null不能宣称旧业务没有价格。

```sql
-- OPERATIONAL GATE ONLY. Confirm source/target DB, backups, paused writers, time source.
-- Replace only after confirming original timestamps; mixed or ambiguous sources mean STOP.
SET @legacy_offset = NULL;
SELECT COUNT(*) AS source_rows FROM energy_prices;
SELECT COUNT(*) AS target_rows_must_be_zero FROM energy_price_hours;
CHECKSUM TABLE energy_prices;
-- Any NULL/invalid conversion or target_rows > 0 means STOP / ROLLBACK.
WITH raw_times AS (
  SELECT energy_prices.*,
    CONVERT_TZ(created_at, @legacy_offset, '+00:00') AS event_utc,
    CONVERT_TZ(updated_at, @legacy_offset, '+00:00') AS modified_utc,
    DATE_FORMAT(CONVERT_TZ(created_at, @legacy_offset, 'Asia/Shanghai'),
      '%Y-%m-%d %H:00:00') AS civil_hour
  FROM energy_prices
), guessed AS (
  SELECT *, CONVERT_TZ(civil_hour, 'Asia/Shanghai', '+00:00') AS hour_guess
  FROM raw_times
), normalized AS (
  -- Shanghai's repeated DST hour has two instants. Choose the earliest (fold=0).
  SELECT *, CASE WHEN CONVERT_TZ(hour_guess - INTERVAL 1 HOUR, '+00:00', 'Asia/Shanghai') = civil_hour
    THEN hour_guess - INTERVAL 1 HOUR ELSE hour_guess END AS hour_start
  FROM guessed
)
SELECT COUNT(*) AS rows_seen, COUNT(DISTINCT hour_start) AS hour_groups,
  SUM(event_utc IS NULL OR modified_utc IS NULL OR hour_start IS NULL
      OR YEAR(event_utc) < 1000 OR YEAR(modified_utc) < 1000
      OR CONVERT_TZ(hour_start, '+00:00', 'Asia/Shanghai') <> civil_hour) AS invalid_rows
FROM normalized;
-- Verify timezone data yields fold=0: civil 1991-09-15 01:00 => UTC 1991-09-14 16:00.
-- Conflict groups and selected old ids are local audit artifacts; never commit them.
WITH raw_times AS (
  SELECT energy_prices.*,
    CONVERT_TZ(created_at, @legacy_offset, '+00:00') AS event_utc,
    CONVERT_TZ(updated_at, @legacy_offset, '+00:00') AS modified_utc,
    DATE_FORMAT(CONVERT_TZ(created_at, @legacy_offset, 'Asia/Shanghai'),
      '%Y-%m-%d %H:00:00') AS civil_hour
  FROM energy_prices
), guessed AS (
  SELECT *, CONVERT_TZ(civil_hour, 'Asia/Shanghai', '+00:00') AS hour_guess
  FROM raw_times
), normalized AS (
  -- Shanghai's repeated DST hour has two instants. Choose the earliest (fold=0).
  SELECT *, CASE WHEN CONVERT_TZ(hour_guess - INTERVAL 1 HOUR, '+00:00', 'Asia/Shanghai') = civil_hour
    THEN hour_guess - INTERVAL 1 HOUR ELSE hour_guess END AS hour_start
  FROM guessed
), ranked AS (
  SELECT *, COUNT(*) OVER (PARTITION BY hour_start) AS group_size,
    ROW_NUMBER() OVER (PARTITION BY hour_start ORDER BY created_at DESC, id DESC) AS rn
  FROM normalized
)
SELECT hour_start, id AS selected_old_id, group_size,
  SUM(group_size > 1) OVER () AS conflict_groups
FROM ranked WHERE rn=1 ORDER BY hour_start;
-- Only execute after all gates pass, with all old/new writers paused.
START TRANSACTION;
SELECT COUNT(*) AS target_rows_must_be_zero FROM energy_price_hours;
INSERT INTO energy_price_hours
  (electric_price, hydrogen_price, argon_price, electric_remark, hydrogen_remark,
   argon_remark, remark, operator, observed_at, hour_start, created_at, updated_at)
WITH raw_times AS (
  SELECT energy_prices.*,
    CONVERT_TZ(created_at, @legacy_offset, '+00:00') AS event_utc,
    CONVERT_TZ(updated_at, @legacy_offset, '+00:00') AS modified_utc,
    DATE_FORMAT(CONVERT_TZ(created_at, @legacy_offset, 'Asia/Shanghai'),
      '%Y-%m-%d %H:00:00') AS civil_hour
  FROM energy_prices
), guessed AS (
  SELECT *, CONVERT_TZ(civil_hour, 'Asia/Shanghai', '+00:00') AS hour_guess
  FROM raw_times
), normalized AS (
  -- Shanghai's repeated DST hour has two instants. Choose the earliest (fold=0).
  SELECT *, CASE WHEN CONVERT_TZ(hour_guess - INTERVAL 1 HOUR, '+00:00', 'Asia/Shanghai') = civil_hour
    THEN hour_guess - INTERVAL 1 HOUR ELSE hour_guess END AS hour_start
  FROM guessed
), ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY hour_start ORDER BY created_at DESC, id DESC) AS rn
  FROM normalized
)
SELECT electric_price, hydrogen_price, argon_price, electric_remark, hydrogen_remark,
  argon_remark, remark, operator, event_utc, hour_start, event_utc, modified_utc
FROM ranked WHERE rn=1;
SELECT COUNT(*) AS imported_hours FROM energy_price_hours;
CHECKSUM TABLE energy_prices;
-- Compare counts, whole groups and times with the selected-old-id manifest.
-- COMMIT only after review; default example explicitly rolls back.
ROLLBACK;
```

SQL默认以ROLLBACK结束，真实导入/COMMIT需独立operational gate。合成数据测试不证明真实MySQL并发或备份恢复。

## 回退与验证

先停新写入、备份小时表。旧追加归档不含切换后新写入，直接回切应用不能恢复这些数据；转回旧追加格式需另行批准并核对。b8d0f2a4c6e8 downgrade仅删除energy_price_hours并丢失全部新数据，真实downgrade/删除/重放另gate。同小时覆盖的旧版本不新增归档，不支持计费重算。

验证复用既有uv/pnpm依赖与本任务公开隔离fixture，完整no_db、compileall、离线Alembic SQL、前端模块check/test/build。真实持久化/唯一键竞争、历史归并与恢复、时钟核对和运行联调均为延后operational gate，源码通过不等于部署。参见[API测试](../../tests/test_energy_price_api.py)。
