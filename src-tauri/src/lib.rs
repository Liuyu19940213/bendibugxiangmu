use std::path::PathBuf;
use std::sync::Mutex;
use tauri::Manager;
use tauri_plugin_shell::ShellExt;

struct PythonProcess {
    child: Mutex<Option<tauri_plugin_shell::process::CommandChild>>,
}

fn resolve_python_and_api(app: &tauri::AppHandle) -> Result<(PathBuf, PathBuf), String> {
    // 1. 优先从 exe 同目录查找（绿色包模式）
    if let Ok(exe_path) = std::env::current_exe() {
        if let Some(exe_dir) = exe_path.parent() {
            let green_python = exe_dir.join("python").join("python.exe");
            let green_api = exe_dir.join("api").join("app.py");
            if green_python.exists() && green_api.exists() {
                return Ok((green_python, green_api));
            }
        }
    }

    // 2. 尝试资源目录（安装包模式）
    if let Ok(res_dir) = app.path().resource_dir() {
        let bundled_python = res_dir.join("python").join("python.exe");
        let bundled_api = res_dir.join("api").join("app.py");
        if bundled_python.exists() && bundled_api.exists() {
            return Ok((bundled_python, bundled_api));
        }
    }

    // 3. 开发模式
    let cwd = std::env::current_dir().map_err(|e| format!("获取当前目录失败: {}", e))?;
    
    let dev_python = cwd.join("src-tauri").join("binaries").join("python").join("python.exe");
    let dev_api = cwd.join("api").join("app.py");
    if dev_python.exists() && dev_api.exists() {
        return Ok((dev_python, dev_api));
    }

    let alt_python = cwd.join("binaries").join("python").join("python.exe");
    let alt_api = cwd.join("api").join("app.py");
    if alt_python.exists() && alt_api.exists() {
        return Ok((alt_python, alt_api));
    }

    Err("无法找到 Python 运行时或 API 代码。请确保资源文件已正确打包。".to_string())
}

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! Welcome to Pixelle-Video.", name)
}

#[tauri::command]
async fn spawn_python(app_handle: tauri::AppHandle) -> Result<String, String> {
    let state: tauri::State<'_, PythonProcess> = app_handle.state();
    let mut child_opt = state.child.lock().map_err(|e| format!("进程锁异常: {}", e))?;
    if let Some(child) = child_opt.take() {
        let _ = child.kill();
    }
    drop(child_opt);

    let (python_path, api_path) = resolve_python_and_api(&app_handle)?;
    let api_dir = api_path.parent().unwrap_or_else(|| std::path::Path::new("."));
    let shell = app_handle.shell();
    let spawn_result = shell.command(python_path.to_str().unwrap_or("python")).args([api_path.to_str().unwrap_or("api/app.py"), "--port", "8000"]).current_dir(api_dir.to_str().unwrap_or(".")).spawn().map_err(|e| format!("启动失败: {}", e))?;

    let child = spawn_result.1;
    let pid = child.pid();
    let mut guard = state.child.lock().map_err(|e| format!("进程锁异常: {}", e))?;
    *guard = Some(child);

    Ok(format!("Python 启动成功 (PID: {:?})", pid))
}

#[tauri::command]
async fn stop_python(app_handle: tauri::AppHandle) -> Result<String, String> {
    let state: tauri::State<'_, PythonProcess> = app_handle.state();
    let mut guard = state.child.lock().map_err(|e| format!("进程锁异常: {}", e))?;
    if let Some(child) = guard.take() {
        child.kill().map_err(|e| format!("终止失败: {}", e))?;
        Ok("Python 已停止".to_string())
    } else {
        Ok("没有正在运行的 Python".to_string())
    }
}

pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_shell::init())
        .manage(PythonProcess { child: Mutex::new(None) })
        .invoke_handler(tauri::generate_handler![greet, spawn_python, stop_python])
        .setup(|app| {
            let app_handle = app.app_handle().clone();
            tauri::async_runtime::spawn(async move {
                let _ = spawn_python(app_handle).await;
            });
            Ok(())
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { .. } = event {
                let app_handle = window.app_handle().clone();
                let _ = tauri::async_runtime::block_on(stop_python(app_handle));
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
