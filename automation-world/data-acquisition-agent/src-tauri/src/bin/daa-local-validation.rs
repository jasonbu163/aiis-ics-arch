//! 显式debug fixture验证入口；裸执行仅帮助，不读取任何默认env/profile。
fn main() {
    std::process::exit(
        aiis_data_acquisition_agent_lib::run_local_validation_command(
            std::env::args().skip(1).collect(),
        ),
    );
}
