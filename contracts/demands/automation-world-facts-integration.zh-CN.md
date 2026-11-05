Contract ID: automation-world-facts-integration
Version: demand-r1
Status: proposed
Consumer: DAA、SMA及其他获选HTTP消费者
Provider: Backend事实模块与各业务模块
Owner Task: ARCH-AW-008 r1

# AW 匿名事实集成与可靠业务投递需求合同

[English](automation-world-facts-integration.md)

## 1. 效力、当前基线与责任

本需求依据 [ARCH-AW-008 r1](../../plans/ARCH-AW-008-stage-c-facts-contract/spec.md) 的精确文档范围批准整理。`proposed` 表示消费者需求已成文，尚不表示 Backend provider 已承诺、实现或验证任何候选 endpoint。后续 Backend 自有 spec 固定正式 schema／参数／算法，并在 published 合同、Pydantic/OpenAPI、Model/Alembic 中对齐；本 Markdown 不是可执行 schema，不授权软件、数据库、设备或实际联调。

[DAA 阶段B](../../automation-world/data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2)已在受控DS范围验收；DAA 当前本地保存，事实上传仍未接通。当前 Backend 有 [raw/latest Model](../../backend/app/monitor/models/monitor.py) 和[受保护 latest GET](../../backend/app/monitor/api/realtime.py)，没有因此具备本需求的新接收与安全游标。旧 CA 的直库 writer 是冻结兼容参考。SMA 保留 TSS 派生／Backend-held 配置基线，不因本需求立即迁入本地 SQLite。

```text
DS/PLC → DAA本地完整提交 → 匿名事实API → raw/latest
                                      ↓ 安全历史/最新读取
                                     SMA → 模块typed集成写入 → 业务可靠提交
                                                                    ↓
                                                          前端认证与权限查询
```

DAA 事实回执与 SMA 业务回执是两个独立持久边界；前者不证明业务入库。各模块API/Service负责业务校验和事务，SMA不连接PLC或业务SQL。

<a id="routes"></a>
## 2. 候选接口与匿名边界

| 方法／候选路径 | 用途 | 本阶段接入要求 |
| --- | --- | --- |
| POST /api/v1/integration/plc-facts/batches | DAA有界批量写入多个PLC/DB样本 | 无登录、JWT、API Key或角色授权 |
| GET /api/v1/integration/plc-facts/latest | 当前结果及派生点位目录 | 同上 |
| GET /api/v1/integration/plc-facts/history | 时间段或持续增量历史 | 同上 |
| POST /api/v1/integration/{module}/{resource} | 后续模块自有typed业务写入模式 | 目标为匿名集成；具体模块另批 |
| 既有前端展示／管理及业务路由 | 现有用途 | 保持各自认证、权限分组、数据范围与业务合同 |

这些路径均是候选，不可据此调用实际服务。匿名规则按路由明确，不按User-Agent、调用方自称DAA/SMA或前端来源动态绕过；不追加隐式白名单、Token或身份平台作为本阶段前置。匿名入口仍检查版本、必填、类型、大小、时间、幂等、顺序与保留，不能接收表名＋任意列直接写SQL；维护、账号、DDL和设备控制不在此通道内。

instanceId／producerId／plcId／sourceGeneration是客户端声明，不证明真实身份或设备所有权。可达客户端能够冒用声明是当前阶段的明确取舍；来源资格／切换是协议和配置约束，不伪称认证安全。现有业务 [温控 POST](../../backend/app/equipment/api/temperature_samples.py) 的认证、完整字段及 [actor参与幂等](../../backend/app/equipment/services/async_temperature_sample.py)仍需模块另行适配；不能伪造admin／用户ID复用。

<a id="identity"></a>
## 3. 身份、类型与现有本地v2的无损关系

| 对象 | 稳定含义与规则 |
| --- | --- |
| pointId | 绑定和点结果身份；名字、IP、DB名不是主键；同PLC移组保留ID |
| sampleId | 首次持久确定的DB包／固定片身份；同ID同内容可确认重复，异内容冲突 |
| cycleId／manifest | 一次组采集及其预期成员／固定片；本批包含若干成员不自动证明整轮齐全 |
| batchId | 一次冻结投递的身份和固定覆盖范围；网络重试不改成员或内容 |
| sourceGeneration＋sourceSeq | 同PLC有效来源代次内的持久顺序；示例序号为十进制字符串，跨PLC不比较 |
| configRevision／定义签名 | 解释当时定义；opaque值不按字符串排新旧，回退不重写历史 |

points字典键保留原pointId字节；[共享响应序列化](../../backend/common/response.py)当前递归改键，后续适配必须区分字段名与数据键。managed点沿用已有ASCII技术命名，sourcePath保留原路径／中文；未显式转换的legacy名字和旧定义无损传输，不强制改名，不当作Rust变量、SQL标识符或脚本执行。

成功值保留JSON数值／布尔等类型；坏质量保留定义、原时间、缺值与reason，不补0／旧值、不省略预期失败点。正式PLC→JSON类型、范围、非有限浮点、整数精度和null矩阵由provider spec固定。本例的精简definition不是当前Point结构的全部字段，不能作为丢弃其他原定义内容的许可。

[本地v2类型](../../automation-world/data-acquisition-agent/src-tauri/src/domain/local_sample.rs)与[持久写入](../../automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/runtime.rs)的对应关系如下。传输投影可另有版本，旧payload/manifest/context原文不变。

| 本地v2字段／证据 | 传输责任 |
| --- | --- |
| schemaVersion=2、sampleId、cycleId、instanceId、plcId | 保留原身份；外层contractVersion不是数据库schemaVersion |
| sourceGeneration、sourceSeq、groupId、revision、dbNumber | 保留源顺序和解释关联；示例用configRevision表达revision，正式别名由provider冻结 |
| points[pointId].definition/value/observedAt/quality/reason | 无损解释；不能把name当ID或丢失失败结果／原时间 |
| startedAt、finishedAt、savedAt、origin及原配置context | 原读取、本地保存、来源语义分别保留；精简样例省略不等于可丢弃，正式schema列清携带或可核实关联 |
| CycleManifest.expectedPointIds/samples/reads | 保留预期点、DB样本及原读取时序；HTTP拆批不改变原应有集合 |
| ManifestSample.sha256与样本原sha256 | 原字节UTF-8 SHA-256；示例sourceSha256仅为原文关联，不等于传输摘要 |

摘要分三层：原payload／manifest／context的原字节SHA-256；版本化传输投影的contentDigest；冻结请求的requestDigest。JSON重新缩进／解析再序列化不能宣称仍是原字节。provider在实施前固定算法、包含／排除字段、字符编码、排序、时间／数值规范化及测试向量；请求摘要的自引用字段如何排除必须明确。携带原文则保留可验证原字节；返回投影则区分原文摘要与投影摘要。

<a id="request"></a>
## 4. 请求、轮次、片段与失败样例

以下全部JSON是合法的**语义占位样例**，ID／摘要／字段及分片编码不承诺通过未来验证器；不是既有可调用schema，不生成或改写本地历史。主例同批三包：A的DB71和DB88属于同一fast轮142，B的DB71属于独立slow轮27；相同DB号不冲突。A的ready失败也作为应有结果保存，因此“成员齐全”和“质量良好”分别判断。

```json
{
  "contractVersion": "plc-facts/v1",
  "batchId": "batch-demo-1",
  "instanceId": "daa-demo",
  "requestDigest": "illustrative-frozen-request-digest",
  "cycles": [
    {
      "plcId": "plc-a",
      "cycleId": "cycle-a-142",
      "sourceGeneration": "generation-a",
      "sourceSeq": "142",
      "groupId": "group-fast",
      "expectedPointIds": [
        "point-a-temperature",
        "point-a-ready",
        "point-a-value"
      ],
      "manifest": [
        {
          "sampleId": "sample-a71",
          "dbNumber": 71,
          "part": 1,
          "parts": 1,
          "contentDigest": "illustrative-transfer-sample-a71"
        },
        {
          "sampleId": "sample-a88",
          "dbNumber": 88,
          "part": 1,
          "parts": 1,
          "contentDigest": "illustrative-transfer-sample-a88"
        }
      ]
    },
    {
      "plcId": "plc-b",
      "cycleId": "cycle-b-27",
      "sourceGeneration": "generation-b",
      "sourceSeq": "27",
      "groupId": "group-slow",
      "expectedPointIds": [
        "point-b-count"
      ],
      "manifest": [
        {
          "sampleId": "sample-b71",
          "dbNumber": 71,
          "part": 1,
          "parts": 1,
          "contentDigest": "illustrative-transfer-sample-b71"
        }
      ]
    }
  ],
  "samples": [
    {
      "sampleId": "sample-a71",
      "cycleId": "cycle-a-142",
      "plcId": "plc-a",
      "sourceGeneration": "generation-a",
      "sourceSeq": "142",
      "groupId": "group-fast",
      "configRevision": "config-a3",
      "dbNumber": 71,
      "sourceSha256": "illustrative-original-sample-a71",
      "points": {
        "point-a-temperature": {
          "definition": {
            "name": "DB71_temperature_Int",
            "sourcePath": "temperature",
            "address": {
              "offset": 2,
              "bit": null
            },
            "dataType": "INT"
          },
          "value": 202,
          "quality": "good",
          "reason": null,
          "observedAt": "2026-11-04T10:00:00.123+08:00"
        },
        "point-a-ready": {
          "definition": {
            "name": "DB71_ready_Bool",
            "sourcePath": "ready",
            "address": {
              "offset": 0,
              "bit": 0
            },
            "dataType": "BOOL"
          },
          "value": null,
          "quality": "bad",
          "reason": "read_timeout",
          "observedAt": "2026-11-04T10:00:00.123+08:00"
        }
      }
    },
    {
      "sampleId": "sample-a88",
      "cycleId": "cycle-a-142",
      "plcId": "plc-a",
      "sourceGeneration": "generation-a",
      "sourceSeq": "142",
      "groupId": "group-fast",
      "configRevision": "config-a3",
      "dbNumber": 88,
      "sourceSha256": "illustrative-original-sample-a88",
      "points": {
        "point-a-value": {
          "definition": {
            "name": "DB88_unit_value_Real",
            "sourcePath": "unit.value",
            "address": {
              "offset": 2,
              "bit": null
            },
            "dataType": "REAL"
          },
          "value": 12.5,
          "quality": "good",
          "reason": null,
          "observedAt": "2026-11-04T10:00:00.123+08:00"
        }
      }
    },
    {
      "sampleId": "sample-b71",
      "cycleId": "cycle-b-27",
      "plcId": "plc-b",
      "sourceGeneration": "generation-b",
      "sourceSeq": "27",
      "groupId": "group-slow",
      "configRevision": "config-b3",
      "dbNumber": 71,
      "sourceSha256": "illustrative-original-sample-b71",
      "points": {
        "point-b-count": {
          "definition": {
            "name": "DB71_count_Int",
            "sourcePath": "count",
            "address": {
              "offset": 2,
              "bit": null
            },
            "dataType": "INT"
          },
          "value": 101,
          "quality": "good",
          "reason": null,
          "observedAt": "2026-11-04T10:00:00.123+08:00"
        }
      }
    }
  ]
}
```

同PLC A另一个slow组可在轮143采DB71的point-a-pressure：它是独立cycle/seq，latest合并该点与fast组的点；不把两个组拼成同步帧，也不以整DB包覆盖另一组。跨PLC和跨DB读取各有原时间，组相同也不保证物理同时。

当前本地v2按DB成包，不证明固定分片已经实现。超大包的候选固定片推演如下；它是场景说明，正式片编码仍需provider定稿。拆分在冻结前决定，每片保留固定身份／摘要／预期点集合；只收到part1时只能确认该片，整轮仍不完整。

```json
{
  "scenario": "fixed-fragments-not-a-wire-schema",
  "plcId": "plc-a",
  "cycleId": "cycle-a-144",
  "sourceSeq": "144",
  "manifest": [
    {
      "sampleId": "sample-a90-part1",
      "dbNumber": 90,
      "part": 1,
      "parts": 2,
      "pointIds": [
        "point-x"
      ],
      "contentDigest": "illustrative-part1"
    },
    {
      "sampleId": "sample-a90-part2",
      "dbNumber": 90,
      "part": 2,
      "parts": 2,
      "pointIds": [
        "point-y"
      ],
      "contentDigest": "illustrative-part2"
    }
  ],
  "receivedSampleIds": [
    "sample-a90-part1"
  ],
  "cycleComplete": false
}
```

缺定义／超限不能临时截断JSON；相同batchId不因重试删点或换片号。按DB逻辑成包不等于一次只许一个HTTP包，首版上传器全实例单在途、有界组批，服务端仍须并发安全。

<a id="receipts"></a>
## 5. 可靠回执、重试与混合批次矩阵

首版整批事务：校验→幂等内容核对→raw新增或确认重复→latest原子条件推进→接收／完整性／安全发布记录→持久提交→回执。跨存储不能同事务时，provider必须先给出等效可靠接收账本合同，不能将易失入队称已提交。

回执绑定版本、batchId、requestDigest及每个确认sample/片的contentDigest，结果区分created／duplicate与整轮完整性。下例中B是同内容重复，A包含坏质量但成员齐全；都已可靠提交。ACK不保证本点latest推进，也不保证跨所有批次的历史前缀齐全。

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "contractVersion": "plc-facts/v1",
    "batchId": "batch-demo-1",
    "requestDigest": "illustrative-frozen-request-digest",
    "status": "committed",
    "results": [
      {
        "sampleId": "sample-a71",
        "contentDigest": "illustrative-transfer-sample-a71",
        "outcome": "created"
      },
      {
        "sampleId": "sample-a88",
        "contentDigest": "illustrative-transfer-sample-a88",
        "outcome": "created"
      },
      {
        "sampleId": "sample-b71",
        "contentDigest": "illustrative-transfer-sample-b71",
        "outcome": "duplicate"
      }
    ],
    "cycles": [
      {
        "cycleId": "cycle-a-142",
        "complete": true
      },
      {
        "cycleId": "cycle-b-27",
        "complete": true
      }
    ]
  }
}
```

DAA校验回执后以短事务单调保存成员ACK和批次结果，提交后才显示已上报。HTTP 200/202、发送完毕、日志、仅持久排队均不是完整事实／业务提交证明。本地ACK失败或后端已存但响应丢失，保持原batch/sample/内容再核实或重试；客户端超时不证明服务端已取消。

| 批次已知状态 | 可确认范围 | 后续处置与原材料保护 |
| --- | --- | --- |
| 整批可靠提交 | 仅回执绑定的成员；完整轮另核manifest | 持久ACK；已有ACK不因其他批超时倒退 |
| 同身份同内容重复 | 有效历史提交证明覆盖的原成员 | 返回等价确认，不增raw、不退latest |
| 同身份异内容 | 本次无新提交；旧提交证明不被否认 | 整批拒绝新提交，保原材料并隔离，不换ID掩盖冲突 |
| 提交结果unknown／丢回执 | 不新增推定ACK，也不推定未提交 | 原冻结请求恢复结果；未核实前不得派生重组或释放引用 |
| 已证明整批无新提交，混合有效／过期成员 | 诊断不是部分ACK；原已有提交证明单独核验 | 原批持久记录拒绝并进入需处理；provider允许退休后，新batchId引用原合法sampleId／原内容，关联parentBatchId／拒绝证明，非法成员仍保护 |
| 成员经其他批次确认，但旧批仍非终结 | 样本ACK单调；旧批身份仍冻结 | 保留重建原请求材料；仅当合同证明无独立批次副作用、完成证据齐全且允许退休时释放旧引用 |
| 样本到期且有仍有效的历史提交证明 | 可返回明确historical confirmation，非当前值可读 | 不恢复raw/latest；本地按历史确认范围记录，不能误标新入库 |
| 样本已到期且无提交证明 | 不可重试拒绝，不伪造ACK | 原样本／拒绝材料保护，不能因过期自动删除；其他合法批次仍获公平机会 |

这是一份责任和持久边界矩阵，不是已实现的退休状态机。Backend/DAA编码前共同固定拒绝证明、旧批终结、派生关系、混合历史重复／过期、人工缺口接受和有限证明保留的精确矩阵。最新优先／公平预算不能跳过这些保护来释放磁盘；无法继续安全保存时明确容量暂停。

以下对应HTTP 409／410／503，业务码为候选。not_committed仅指该次请求无新提交，不否认以前已经提交；unknown不能解读为已回滚。其余非法格式／类型／超限的HTTP与业务码由provider定稿；集成接口尊重HTTP语义，客户端按status/code/errorCode及结构化结果判断，不依赖message文本。

```json
{
  "code": 409,
  "message": "conflict",
  "errorCode": "facts.sample_content_conflict",
  "data": {
    "batchId": "batch-conflict",
    "retryable": false,
    "persistence": "not_committed",
    "sampleIds": [
      "sample-a71"
    ]
  }
}
```

```json
{
  "code": 410,
  "message": "expired",
  "errorCode": "facts.sample_expired",
  "data": {
    "batchId": "batch-expired",
    "retryable": false,
    "persistence": "not_committed",
    "sampleIds": [
      "sample-old"
    ]
  }
}
```

```json
{
  "code": 503,
  "message": "temporarily_unavailable",
  "errorCode": "facts.commit_outcome_unknown",
  "data": {
    "batchId": "batch-unknown",
    "retryable": true,
    "persistence": "unknown"
  }
}
```

<a id="latest"></a>
## 6. latest、定义与来源顺序

raw是去重后的追加事实；latest语义按稳定PLC/pointId独立维护、按DB聚合。建议逐点物理latest；实际表名、索引、辅助账本及旧PLC/DB/group表兼容归Backend，不限制数据库只许两张表。

推进需同时满足有效来源代次、有效定义／成员声明、更高本点sourceSeq和未过期，并用数据库原子条件更新或等效并发控制；先查后无条件写不合格。HTTP到达／接收时间、可回拨采集时间、opaque代次或revision的字符串大小均不是新旧顺序。某点更高seq不能跳掉另一点合法较低seq；单包缺点不当删除。

首次采用、冲突来源、旧代次截止／新代次基线和定义起效由provider在软件spec定稿。正常重启／换周期／移组不清零持久序号；旧代次可按资格补raw，但不自动获得latest接管。匿名下“有效来源选择”是声明／配置约束，不能声称证明设备所有权。

latest取“最近结果”：新顺序的bad结果更新观察时间、quality、reason和缺值，旧好值仅可另带原身份／时间作历史参考。显式停用／退役／定义变化可随同一事实入口的受限成员声明表达，编码另定；没有声明时，只能陈旧／到期，不能立即推断停用。旧历史不能复活旧成员或回退类型／地址。

下例asOf只表示查询时刻，observedAt才是采集事实时间。SMA按自己的最大年龄和quality判断；在三个月内不等于实时新鲜。点位目录从这些有效当前定义派生，只有已上报点，不另存无值pointCatalog。

聚合后每点必须保留原sampleId、有效来源代次／序号及定义版本关联，供SMA生成稳定sourceRefs。下例source对象仅示意，正式编码由provider spec冻结；definitionVersion不代表当前本地v2已新增字段。

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "asOf": "2026-11-04T10:00:01.000+08:00",
    "items": [
      {
        "plcId": "plc-a",
        "dbNumber": 71,
        "points": {
          "point-a-temperature": {
            "definition": {
              "name": "DB71_temperature_Int",
              "sourcePath": "temperature",
              "address": {
                "offset": 2,
                "bit": null
              },
              "dataType": "INT"
            },
            "value": 202,
            "quality": "good",
            "reason": null,
            "observedAt": "2026-11-04T10:00:00.123+08:00",
            "source": {
              "sampleId": "sample-a71",
              "cycleId": "cycle-a-142",
              "groupId": "group-fast",
              "sourceGeneration": "generation-a",
              "sourceSeq": "142",
              "configRevision": "config-a3",
              "definitionVersion": "illustrative-definition-a3"
            }
          },
          "point-a-ready": {
            "definition": {
              "name": "DB71_ready_Bool",
              "sourcePath": "ready",
              "address": {
                "offset": 0,
                "bit": 0
              },
              "dataType": "BOOL"
            },
            "value": null,
            "quality": "bad",
            "reason": "read_timeout",
            "observedAt": "2026-11-04T10:00:00.123+08:00",
            "source": {
              "sampleId": "sample-a71",
              "cycleId": "cycle-a-142",
              "groupId": "group-fast",
              "sourceGeneration": "generation-a",
              "sourceSeq": "142",
              "configRevision": "config-a3",
              "definitionVersion": "illustrative-definition-a3"
            }
          }
        }
      }
    ]
  }
}
```

SMA定义签名含name／地址／类型／有效性，排除value／quality／时间／sampleId／sourceSeq。真实定义变化只暂停受影响绑定；无关revision变化不全停。旧历史按原定义和获准映射版本处理。DAA仍报旧定义时，不能仅凭JSON自动检测PLC实际程序漂移。

<a id="history"></a>
## 7. 一个history接口的range与changes模式

| 模式 | 候选查询参数及范围 | 分页／使用规则 |
| --- | --- | --- |
| range | mode=range、PLC/DB/point筛选、from、to、limit、pageCursor | 按原点observedAt；候选半开[from,to)，时间为+08；固定排序／查询快照边界，返回nextPageCursor，供人工查看／指定范围回算 |
| changes | mode=changes、固定筛选、cursor、limit | 按Backend可靠发布位置，返回nextCursor/hasMore及来源／样本／完整性，供持续消费，包括晚补传 |

参数名、允许筛选、快照边界和limit由provider正式spec冻结；range的页游标不能作为changes接收游标。两类游标绑定模式、合同版本和过滤条件，不能换PLC／过滤后继续沿用。未指定时间的changes首次起点须显式选择最早可恢复位置或带审计的新基线；不能默默从尾部开始却称全量。

非空增量页复用第4节语义样本，不把查询投影冒称原样本字节；下面只示一包。它可能晚于sourceSeq=145的包才提交，cursor仍须覆盖它。

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "mode": "changes",
    "items": [
      {
        "sampleId": "sample-a71",
        "cycleId": "cycle-a-142",
        "plcId": "plc-a",
        "sourceGeneration": "generation-a",
        "sourceSeq": "142",
        "groupId": "group-fast",
        "configRevision": "config-a3",
        "dbNumber": 71,
        "sourceSha256": "illustrative-original-sample-a71",
        "points": {
          "point-a-temperature": {
            "definition": {
              "name": "DB71_temperature_Int",
              "sourcePath": "temperature",
              "address": {
                "offset": 2,
                "bit": null
              },
              "dataType": "INT"
            },
            "value": 202,
            "quality": "good",
            "reason": null,
            "observedAt": "2026-11-04T10:00:00.123+08:00"
          },
          "point-a-ready": {
            "definition": {
              "name": "DB71_ready_Bool",
              "sourcePath": "ready",
              "address": {
                "offset": 0,
                "bit": 0
              },
              "dataType": "BOOL"
            },
            "value": null,
            "quality": "bad",
            "reason": "read_timeout",
            "observedAt": "2026-11-04T10:00:00.123+08:00"
          }
        }
      }
    ],
    "nextCursor": "opaque-commit-safe-cursor-example",
    "hasMore": true
  }
}
```

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "mode": "changes",
    "items": [],
    "nextCursor": "opaque-commit-safe-cursor-example",
    "hasMore": false
  }
}
```

空页／hasMore=false只说明该次可交付页，不能证明没有在途事务、没有采集缺口或所有sourceSeq已连续完整。10:20提交原时间10:05的样本必须能在后续changes页读到；仅记最大采集时间会漏它。

Backend须证明cursor之前的可交付提交以后不会才出现。较小raw自增ID可先分配后提交，max(raw.id)、最大sourceSeq、查询最大时间未经证明都不能当安全cursor；选择提交有序发布、缺口感知或等效机制与并发验证归Backend。过滤自然跳号不等于缺失，完整轮前缀、最大已见序号和接收cursor分别解释。

cursor过期／筛选或合同改变／材料已删除时，明确错误原因、可恢复起点／范围、受影响缺口和显式重同步流程；不静默跳尾。重同步保留已处理与业务确认，不为重取的相同输入重新造eventId。SMA接收cursor不等于处理checkpoint；有状态／窗口算法另定源序、完整性、迟到和gap政策。

<a id="retention"></a>
## 8. 上海时间、三自然月与有界证明

Backend事实时间、新API／IPC按Asia/Shanghai、RFC3339携带+08:00，保留原精度；UI默认24小时到秒。原观察、读取起止、本地保存、后端提交与界面刷新时间分开；外部其他时区在接入边界转换一次。旧UTC／未知profile不因此获准迁移，不能整体加八小时或改历史字节。

raw/latest默认且最多三个自然月，可设更短。每点最大截止=原observedAt加三自然月，月末无对应日时取目标月末同一上海墙上时刻，t达到截止即不可作为有效事实读取；不是90天。上传、查询、ACK、其他点／组更新均不续期。未来时间按provider允许偏差明确拒绝／隔离，不改写成接收时间。

| 原observedAt | 最大截止 |
| --- | --- |
| 2026-01-31T12:00:00.123+08:00 | 2026-04-30T12:00:00.123+08:00 |
| 2023-11-30T06:00:00.000+08:00 | 2024-02-29T06:00:00.000+08:00 |
| 2024-11-30T06:00:00.000+08:00 | 2025-02-28T06:00:00.000+08:00 |

一包含不同observedAt时，整包不可变原文读取默认按最早成员截止保守到期；latest各点独立到期。等效投影／存储策略须在Backend spec证明不返回过期值，区分原文与投影及其摘要，不能因其他点仍有效而通过原文泄露到期值。不可变原文并不授权超期可读。

逻辑不可读、分批物理删除、空间回收／备份／副本职责分别定义；清理SLA、批量／锁／负载预算和失败日志由Backend固定，不声称截止瞬间擦除所有介质。最小幂等／历史回执／完整性摘要可按独立有限期限保留，不能永久保存原值；已过期重复不得复活raw/latest。证明缺失时不伪造历史ACK。

长期无新事实的latest及派生目录会到期。后端不因DAA/SMA尚未确认而延长事实窗口；本地未确认／未完成／冻结引用仍保护，拒绝不是本地删除许可。有限磁盘与长断网可能导致容量暂停或真实缺口，不能承诺无限补传。

<a id="business"></a>
## 9. SMA映射、业务回执与永久业务数据

SMA读取latest做状态／预览，读取history做逐样本／历史计算；选择点、校验定义／质量／年龄，按OpenAPI或手工目标配置映射成模块typed data。DAA包不强制对应一次业务请求；跨DB/PLC拼对象须记录各输入身份与时间差，不能虚构同步快照。

下面拟新增单温度接口的语义请求不是现有完整温控POST可调用体。producer声明与eventId定义一次逻辑投递，mappingRevision冻结语义，sourceRefs解释输入；相同已处理输入不因下一次定时轮询而新造输出。不同真实样本／窗口／获准修正可有自己的逻辑事件，规则由模块合同定义。

```json
{
  "producerId": "sma-demo",
  "eventId": "delivery-demo-1",
  "mappingId": "mapping-temperature",
  "mappingRevision": "mapping-v3",
  "sourceRefs": [
    {
      "plcId": "plc-a",
      "sampleId": "sample-a71",
      "pointId": "point-a-temperature",
      "sourceGeneration": "generation-a",
      "sourceSeq": "142",
      "configRevision": "config-a3",
      "definitionVersion": "illustrative-definition-a3"
    }
  ],
  "data": {
    "equipmentId": "equipment-demo",
    "sampledAt": "2026-11-04T10:00:00.123+08:00",
    "temperature": 202
  }
}
```

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "producerId": "sma-demo",
    "eventId": "delivery-demo-1",
    "requestDigest": "illustrative-business-request-digest",
    "recordId": "business-record-demo",
    "outcome": "created",
    "persistence": "committed"
  }
}
```

目标必须校验模块必填／范围／设备／业务自然键，声明幂等作用域／期限；同producer/event同内容返回等价提交结果，不同内容冲突。已有sampleId幂等接口需定义与eventId的等价映射，不并存两套含义不明身份。SMA持久冻结请求，提交后的业务回执核对并本地保存才标已投递；HTTP 200/202或仅入队不是业务永久入库。

接收cursor、处理checkpoint、冻结outbox、各目标回执分开。目标A已确认、B未确认只恢复B；丢回执按原eventId核实／重试，不能盲目换键。unknown和目标无幂等／核实能力须明确处置，不承诺任意外部副作用恰好一次。

已经业务API校验并可靠确认的记录默认永久保存，即无自动到期删除；修正／删除仍按模块业务规则。业务表自带实际业务值、事件时间及必要来源／定义／映射版本，即使raw过期也能解释，不仅保存raw外键。raw/latest清理不级联删除业务记录、未完成outbox和仍有效最小证明；业务追溯不等于永久复制全部raw原文。

SMA在源到期前已可靠保存足够输入／输出时，按自身容量／期限及目标合同继续处理投递；尚未取得的输入／缺片已到期则报告缺口、暂停受影响规则并显式重同步，永久业务政策不能补造未入库数据。SMA本地输入／outbox有界，不能成为无限原始备份；SMA存储位置和迁库由其自有任务决定。

<a id="implementation"></a>
## 10. 后续任务、依赖与验收材料

共同需求文档完成独立文档核验及Owner文档终验后，Backend provider另立精确spec固定正式版本／算法／限额及published合同。DAA固定消费该版本，两端各自批准后可以并行开发，实际HTTP联调等待Backend固定就绪候选。共同语义实质改变须修订受影响spec并重新精确批准。

| 后续owner／候选任务 | 必须覆盖的交付／验收材料 |
| --- | --- |
| Backend／暂拟ARCH-BE-009 | B01匿名严格一写两读；B02显式schema迁移及旧CA/Projection兼容；B03事务／重复／冲突／unknown／混合回执；B04逐点并发latest与定义来源；B05安全游标和晚提交；B06时区／到期／清理／有限证明；B07获批隔离库验证与fresh QA；B08固定合同／源码／schema／指纹／限额／错误／测试材料的真实就绪交接 |
| DAA／暂拟DAA-008 | D01单一目标／周期与SQLite配置；D02Rust有界单在途调度；D03冻结与可靠本地ACK恢复；D04最新优先与公平补传；D05采集上报独立控制／容量／启动停止；D06工作台真实状态／有界日志／CU；D07显式投递元数据升级与历史保护；D08双语手册、必要Owner原生增量操作、同库对账和fresh QA |
| SMA／各业务模块 | 单独批准消费／映射／持久业务投递及匿名typed模块入口；不是DAA阶段C前置，不由本需求授权实现 |

编号和完整标准引用 [获批spec第8节](../../plans/ARCH-AW-008-stage-c-facts-contract/spec.md#8-后续软件任务依赖与验收标准)。这些候选ID当前没有在本任务中创建；软件／schema／实际联调仍未执行。DAA阶段C完成须有Backend就绪、可靠上传／恢复、双方事实对账和Owner决定；自动启动、后台托管、真实现场、生产迁移及跨平台打包另批。

正式软件spec进入编码前，还须冻结：PLC/JSON类型与缺值矩阵、片段编码、三类摘要profile、来源首次采用／交接及定义起效、游标算法／起止与过滤、时钟容差、请求／速率／公平／超时预算、混合批次退休、清理SLA和最小证明期限。本文不通过占位例子隐式选择依赖库、数据库物理布局或运行参数。
