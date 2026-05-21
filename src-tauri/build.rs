fn main() {
    println!("cargo:rerun-if-changed=tauri.conf.json");
    println!("cargo:rerun-if-env-changed=TAURI_CONFIG");

    let target_os = std::env::var("CARGO_CFG_TARGET_OS").unwrap_or_default();
    match target_os.as_str() {
        "windows" | "linux" | "macos" | "dragonfly" | "freebsd" | "netbsd" | "openbsd" => {
            println!("cargo:rustc-cfg=desktop");
        }
        "android" | "ios" => {
            println!("cargo:rustc-cfg=mobile");
        }
        _ => {
            println!("cargo:rustc-cfg=desktop");
        }
    }

    let profile = std::env::var("PROFILE").unwrap_or_default();
    if profile == "debug" {
        println!("cargo:rustc-cfg=dev");
    }

    println!("cargo:rustc-check-cfg=cfg(dev)");
    println!("cargo:rustc-check-cfg=cfg(desktop)");
    println!("cargo:rustc-check-cfg=cfg(mobile)");

    if target_os == "windows" {
        println!("cargo:rustc-env=WINAPI_TARGET_TRIPLET=x86_64-pc-windows-msvc");
    }
}
