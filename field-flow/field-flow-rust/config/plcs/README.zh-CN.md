# PLC文件

[English](README.md)

每PLC一个闭合ff.plc JSON对象，schema_version=1，与主YAML v2/SQLite schema1独立。[s7-a.json](s7-a.json)/[s7-b.json](s7-b.json)是固定合成S7；[modbus-example.json](modbus-example.json)仅结构校验，不能run，34502不属于夹具端口。按[目录教程](../../USER_GUIDE.zh-CN.md#catalog-v2)操作。

JSON为UTF-8无BOM；拒重复/未知键、null冒充缺省、隐式类型、整数浮点/指数词法、超过16层嵌套。主文件≤64KiB，1–4唯一相对非symlink路径；每PLC≤1MiB、总≤4MiB、≤4096点、≤64 DB或4 table。ID为1–64字节ASCII字母/数字/_/-。包括disabled/未引用声明都完整校验。重复设备/点身份、物理重叠、共享host:port失败。同网关不同Modbus Unit ID不是独立链路（shared_transport_unsupported）。

公共必填format/schema_version/id/protocol/source/connection，且s7恰有dbs，modbus_tcp恰有tables。可选name/display_name/description限128/256/1024 UTF-8字节；metadata仅brand/model/firmware各≤128。点说明name/display_name/source_name/source_path/source_native_type为可选非空字符串，限128/256/256/1024/32。点由ID/地址选择，不由显示名/厂家/文件名选择。

S7 connection必填规范单播IPv4、port1–65535、rack0–7、slot0–31。可选local_tsap/remote_tsap1–65535，缺省256及256+rack×32+slot。非默认TSAP结构有效，但runtime_compatible=false/run exit2。DB number1–65535、size_bytes2–65536、enabled缺省true、points非空。点必填id/data_type=int16/byte_offset0–65534，可选enabled；offset+2≤size。INT为有符号16位大端。BOOL/bit/scale/word_order不属于S7 v1。声明大小不证明现场布局/写许可。

Modbus connection仅host/port/unit_id1–255。table四类coils/discrete_inputs/holding_registers/input_registers；pdu_address零基，不从40001自动换算。每functions必有read/write（write可null）。coils bool为1/null或5；discrete bool为2/null；holding int16/uint16为3/null或6；input int16/uint16为4/null。register的int32/uint32/float32占两register，必须high_word_first/low_word_first且write=null。拒其他类型/FC15/16/width/quantity，末地址≤65536，无重叠。bool/16位拒word_order。register可选scale必须factor/offset有限且绝对值≤1e9，factor非零；bool拒scale。这些声明不实现Modbus wire/client/codec，也不授写权限。

manual来源必有kind=manual，可选note≤512。DS来源必有kind=device_simulator、export_mode=saved_revision、instance_id=设备id、revision{id=规范小写UUID,saved_seq=1..9007199254740991,payload_sha256=64位小写hex}、非空exporter_version≤64及generated_at RFC3339+08:00。可选runtime_observation必有observed_at+08、selected_revision、loaded_revision；后二者为revision对象或显式null。缺事实省略观测，saved/selected/loaded分开。FF只校验声明/hash，不证明DS数据库事实。DS当前没有导出器；未来DS须明确确认可达connect host和TSAP方向。来源、原revision payload SHA、冻结JSON原字节hash都是溯源，不是效果身份。

主v2含instance_id/plc_files/plc_runtime/flows/http/shutdown_timeout_ms。每plc_runtime有device_id及原五预算，每文件ID恰有一预算。flow必有id/business_name/interval_ms/device_ids；demo01另有source_id/get_url/input_max_age_ms/target{device_id,point_id}；read_points改为reads1–16唯一enabled且属于子集的引用，无伪造HTTP/target。预算区间和启动规则见[指南](../../USER_GUIDE.zh-CN.md)。validate只读；结构有效但能力不兼容exit0，run在State.open前拒绝。
