//! 文件：src/main.rs；只启动CLI/私有driver入口，无业务或设备IO。
#[tokio::main]
async fn main() {
    let code = field_flow::commands::execute(std::env::args().skip(1).collect()).await;
    std::process::exit(code);
}
