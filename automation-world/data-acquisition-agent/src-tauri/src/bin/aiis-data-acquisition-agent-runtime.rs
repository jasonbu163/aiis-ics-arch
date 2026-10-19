//! 退役headless入口：不加载配置、不获取锁、不执行旧服务。
fn main() {
    std::process::exit(aiis_data_acquisition_agent_lib::run_headless_runtime());
}
