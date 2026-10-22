// 薄桌面build桥：消费runtime links元数据，不要求用户预构建native。
fn main() {
    tauri_build::build();
    if std::env::var_os("CARGO_FEATURE_NATIVE_S7").is_some() {
        let directory = std::env::var("DEP_DS_S7_NATIVE_LIBDIR")
            .expect("ds-runtime native build metadata missing");
        println!("cargo:rustc-link-arg=-Wl,-rpath,{directory}");
    }
}
