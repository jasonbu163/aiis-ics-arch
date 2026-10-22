# 组件声明

本工程手写代码沿用仓库LICENSE中的MIT，不重新许可第三方依赖。

Cargo.lock固定crates.io的rust-snap7 1.142.2。包字段/Rust包装声明MulanPSL-2.0；所带native Snap7源码保留LGPL-3.0-or-later头，build.rs另有GPL-3.0-or-later头。上游构建把native C++编译/链接进本可执行文件。三者声明存在差异，不能只用包字段代替全组件许可判断；原声明保留在未修改依赖制品中，本工程不vendor/patch第三方。

有限INT payload adapter为本工程手写，经公开ISO exchange API调用，不复制上游协议实现。其余Tokio/reqwest/serde/rusqlite等精确来源/checksum归Cargo.lock，SQLite使用rusqlite bundled构建。工件分发、静态链接合规核查、打包/签名及现场交付均需独立gate，本任务不发布工件。
