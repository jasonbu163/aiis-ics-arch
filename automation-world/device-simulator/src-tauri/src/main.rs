// DS原生薄壳：固定裸程序身份；业务实现归ds-runtime。
// Tauri在dev模式自行嵌入plist；production裸Mach-O补同一身份，不创建.app或授予权限。
#[cfg(all(target_os = "macos", not(dev), not(feature = "test-automation")))]
tauri::embed_plist::embed_info_plist_bytes!(br#"<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleIdentifier</key><string>com.aiis.aw.devicesimulator</string>
<key>CFBundleName</key><string>AIIS Device Simulator</string>
<key>CFBundleDisplayName</key><string>AIIS Device Simulator</string>
<key>CFBundleExecutable</key><string>aiis-device-simulator</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleShortVersionString</key><string>0.1.0</string>
<key>CFBundleVersion</key><string>0.1.0</string>
</dict></plist>"#);
#[cfg(all(target_os = "macos", not(dev), feature = "test-automation"))]
tauri::embed_plist::embed_info_plist_bytes!(br#"<?xml version="1.0" encoding="UTF-8"?><plist version="1.0"><dict><key>CFBundleIdentifier</key><string>com.aiis.aw.devicesimulator.validation</string><key>CFBundleName</key><string>AIIS Device Simulator</string><key>CFBundleExecutable</key><string>aiis-device-simulator</string><key>CFBundlePackageType</key><string>APPL</string><key>CFBundleShortVersionString</key><string>0.1.0</string><key>CFBundleVersion</key><string>0.1.0</string></dict></plist>"#);
fn main() {
    #[cfg(not(feature = "test-automation"))]
    if std::env::args().len() != 1 {
        eprintln!("AIIS Device Simulator: product entry accepts no test arguments");
        std::process::exit(2)
    }
    aiis_device_simulator_lib::run()
}
