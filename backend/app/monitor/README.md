# Monitor facts and business history

[中文版本](README.zh-CN.md)

Core collector/status and realtime/latest retain the original three Models and `monitor` permission. `app.monitor.models:PlcDbBlockRawSnapshot` is a public read-only Model export for explicit model_requires consumers; this exposes no collector writer or new API.

The separate `/monitor/temperature` and `/monitor/energy` GETs require `monitor-business-read`. Neither key grants the other surface. These queries read the two business history tables and never persist diagnostic samples, including when business mock configuration is enabled. Empty curves remain empty. The process-curve synchronous Projection descriptor is local and caller-transaction owned; discovery never starts it or publishes mapping.

Only HistoryProcessCurve and HistoryEnergyConsumption supplement the three Core Models; the twelve former HMI/deprecated/alarm/tracking Models are excluded. See the [public contract](../MODULE_CONTRACT.md). The explicit schema successor and source checks require separate MySQL/runtime gates before adoption; no CA/PLC operations are implied.


## External process curves

POST/GET `/monitor/process-curve-samples` uses the independent `monitor-curve-ingest/read` permissions and
`MONITOR_MAPPING_INGEST_ID` scope. POST appends immutable source samples, at least one of the existing 33
measurements; twelve temperatures are signed integers, twenty-one values are FLOAT measurements. coilNumber is
optional. Same source millisecond with different content or field presence returns 409; accepted curves are not
overwritten. This does not write energy summaries or create performance parents.

GET requires equipmentId and exact YYYY-MM-DD in Asia/Shanghai; UTC sampled_at is filtered by that natural day.
Optional recordId and limit 1–1000 (default 1000) select the latest samples, returned ascending as complete items,
trends and latest. Empty results are [], [] and {}. All four charts preserve missing values as gaps/missing symbols.
The curve page persists legacy/http source and equipment in the URL; HTTP scope/data failures never fall back.
The old temperature endpoint reads only NULL equipment rows using its existing created_at date semantics.
Collector/raw/latest and energy surfaces keep their original source and permissions.
