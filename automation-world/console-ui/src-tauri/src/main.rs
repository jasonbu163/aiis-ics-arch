//! Console UI 原生入口：仅启动桌面工作台，不解析工业参数。
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
fn main() {
    aiis_aw_console_ui_lib::run()
}
