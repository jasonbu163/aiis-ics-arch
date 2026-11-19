# 旧设备与过程观测回归证据

这里逐字节保全退役前的三个混合套件。原路径为 backend/tests/ 下同名 Python 文件。文件末尾的 .txt 表示历史源码材料。当前回归由 test_observation_retirement.py、test_equipment_observation_r10_flow.py 及角色和迁移测试承担。

| 原文件 | 被验证的历史入口 | SHA-256 |
| --- | --- | --- |
| test_business_integration_service.py | BE-010 旧设备量型接收、旧过程曲线、冲突、回执和提交未知。已退役 coil 实绩用例保留原 skip。 | 0186af3dd075a16fb851412cdaef1d89965e67ca7149f94b9af49d5b5fa6f9cb |
| test_mapping_api.py | BE-006 旧设备三个采样 HTTP 路径、旧过程曲线 HTTP、原认证和异常边界。已退役旧实绩 HTTP 用例保留原 skip。 | 434b6c18007da5d2b1d4c19c2a870f4fb470600d1e34fad9237052a730061072 |
| test_mapping_service.py | BE-006 对应旧设备／过程服务、旧事务和回执竞争。原 skip 的旧实绩观察和采样保持原声明。 | 5261b4198b11c65178aef76ca94deb7ba3674892227cc25f08672b29c0f94aa8 |

复现用精确 Git 源码 f7c5608c0e433612b15821a578a7ef3e4f155cdb，导出 backend 和 contracts 至专用临时目录。以项目现有 Python 环境和合成 no_db 配置在导出副本 backend 下执行：

```bash
python -m pytest tests/test_business_integration_service.py tests/test_mapping_api.py \
  tests/test_mapping_service.py -m no_db -q --tb=short
```

2026-11-18 Development 在该固定源码复跑，75 通过，21 保持原 skip。历史映射的 API 和 Service 测试相互依赖，始终配套复验。
