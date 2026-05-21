/**
 * useTauriCommand — Tauri IPC 命令封装
 * 统一封装 invoke 调用，处理加载/错误状态
 */
import { ref } from 'vue';
import { invoke } from '@tauri-apps/api/core';

export function useTauriCommand() {
  const loading = ref<boolean>(false);
  const error = ref<string | null>(null);

  /**
   * 通用 invoke 封装
   * @param command - Rust 侧命令名
   * @param args - 可选参数对象
   * @returns 命令返回值或 null（出错时）
   */
  async function call<T>(
    command: string,
    args?: Record<string, unknown>,
  ): Promise<T | null> {
    loading.value = true;
    error.value = null;
    try {
      const result = await invoke<T>(command, args);
      return result;
    } catch (e: unknown) {
      const msg: string =
        typeof e === 'string' ? e : (e as Error)?.message || 'Tauri 命令执行失败';
      error.value = msg;
      return null;
    } finally {
      loading.value = false;
    }
  }

  // ---- 常用命令 ----

  /** 启动 Python 服务 */
  async function startPythonServer(): Promise<boolean | null> {
    return call<boolean>('start_python_server');
  }

  /** 停止 Python 服务 */
  async function stopPythonServer(): Promise<boolean | null> {
    return call<boolean>('stop_python_server');
  }

  /** 查询 Python 服务状态 */
  async function pythonStatus(): Promise<string | null> {
    return call<string>('python_status');
  }

  /** 打开目录选择对话框，返回所选路径 */
  async function selectDirectory(): Promise<string | null> {
    return call<string>('select_directory');
  }

  /** 打开文件选择对话框 */
  async function selectFile(extensions?: string[]): Promise<string | null> {
    return call<string>('select_file', { extensions });
  }

  /** 读取文本文件内容 */
  async function readTextFile(path: string): Promise<string | null> {
    return call<string>('read_text_file', { path });
  }

  return {
    loading,
    error,
    call,
    startPythonServer,
    stopPythonServer,
    pythonStatus,
    selectDirectory,
    selectFile,
    readTextFile,
  };
}
