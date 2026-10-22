// DS native构建桥：正式源码自动CMake编译，向桌面直接依赖传递libdir。
use std::{env, path::Path, process::Command};

fn run(command: &mut Command) {
    let status = command
        .status()
        .expect("native build tool unavailable; install README prerequisites");
    assert!(status.success(), "DS native build failed: {command:?}");
}

fn main() {
    for key in [
        "CXX",
        "CXXFLAGS",
        "SDKROOT",
        "DEVELOPER_DIR",
        "MACOSX_DEPLOYMENT_TARGET",
        "PATH",
    ] {
        println!("cargo:rerun-if-env-changed={key}");
    }
    if env::var_os("CARGO_FEATURE_NATIVE_S7").is_none() {
        return;
    }
    assert_eq!(
        env::var("TARGET").unwrap(),
        "aarch64-apple-darwin",
        "native target not validated; no stub fallback"
    );
    let source = Path::new(&env::var("CARGO_MANIFEST_DIR").unwrap())
        .join("../native")
        .canonicalize()
        .expect("formal native source");
    println!("cargo:rerun-if-changed={}", source.display());
    let out = env::var("OUT_DIR").unwrap();
    let build = Path::new(&out).join("native-build");
    let libdir = Path::new(&out).join("native");
    let sdk = Command::new("/usr/bin/xcrun")
        .arg("--show-sdk-path")
        .output()
        .expect("macOS SDK required");
    assert!(sdk.status.success(), "xcrun SDK lookup failed");
    let sdk = String::from_utf8(sdk.stdout).unwrap();
    println!("cargo:rerun-if-changed={}/SDKSettings.json", sdk.trim());
    run(Command::new("cmake")
        .arg("-S")
        .arg(&source)
        .arg("-B")
        .arg(&build)
        .args([
            "-G",
            "Unix Makefiles",
            "-DCMAKE_MAKE_PROGRAM=/usr/bin/make",
            "-DCMAKE_CXX_COMPILER=/usr/bin/clang++",
            "-DCMAKE_OSX_ARCHITECTURES=arm64",
            "-DCMAKE_BUILD_TYPE=RelWithDebInfo",
        ])
        .arg(format!("-DCMAKE_OSX_SYSROOT={}", sdk.trim()))
        .arg(format!(
            "-DCMAKE_CXX_FLAGS={}",
            env::var("CXXFLAGS").unwrap_or_default()
        ))
        .arg(format!("-DDS_NATIVE_OUTPUT_DIR={}", libdir.display())));
    run(Command::new("cmake")
        .arg("--build")
        .arg(&build)
        .args(["--parallel", "2"]));
    assert!(
        libdir.join("libds_s7_native.dylib").is_file(),
        "native dylib missing"
    );
    println!("cargo:libdir={}", libdir.display());
    println!("cargo:rustc-link-search=native={}", libdir.display());
    println!("cargo:rustc-link-lib=dylib=ds_s7_native");
    println!("cargo:rustc-link-arg=-Wl,-rpath,{}", libdir.display());
}
