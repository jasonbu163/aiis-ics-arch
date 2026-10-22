# TIA fixtures v1

手写公开names.db/names.udt和算法前独立冻结的expected-v1.json定义命名fixture v1，合成DB映射Names28=28、Names60=60、Names47=47。每个expected-v1 case为独立namespace，flatten碰撞batch另列。无客户源或实际端点。daa005-layout-oracle.json逐字镜像原DAA-005 oracle，SHA-256 `2f2f6fe79eea60b48357b72f8a4f352016da4c8d95220ba2e06005133c24e633`；原文件仍是单一布局规则版本，镜像不得独立修改/重排。消费者用自己的既有JSON reader，核心测试仅std；交付全hash归DAA-006 tasks。
