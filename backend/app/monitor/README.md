# Monitor facts and business history

[中文版本](README.zh-CN.md)

Core collector/status and realtime/latest retain the original three Models and `monitor` permission. `app.monitor.models:PlcDbBlockRawSnapshot` is a public read-only Model export for explicit model_requires consumers; this exposes no collector writer or new API.

The separate `/monitor/temperature` and `/monitor/energy` GETs require `monitor-business-read`. Neither key grants the other surface. These queries read the two business history tables and never persist diagnostic samples, including when business mock configuration is enabled. Empty curves remain empty. The process-curve synchronous Projection descriptor is local and caller-transaction owned; discovery never starts it or publishes mapping.

Only HistoryProcessCurve and HistoryEnergyConsumption supplement the three Core Models; the twelve former HMI/deprecated/alarm/tracking Models are excluded. See the [public contract](../MODULE_CONTRACT.md). The explicit schema successor and source checks require separate MySQL/runtime gates before adoption; no CA/PLC operations are implied.
