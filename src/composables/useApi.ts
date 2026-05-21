/**
 * useApi — HTTP 请求封装
 * 对 fetch 的轻量封装，统一处理错误和 ApiResponse 格式
 */
import { ref } from 'vue';
import type { ApiResponse } from '@/types';

export function useApi() {
  const loading = ref<boolean>(false);
  const error = ref<string | null>(null);

  /**
   * 通用请求方法
   * @param url - 请求 URL
   * @param options - fetch 配置（自动合并 Content-Type 头）
   * @returns 统一响应格式 ApiResponse<T>
   */
  async function request<T>(
    url: string,
    options?: RequestInit,
  ): Promise<ApiResponse<T>> {
    loading.value = true;
    error.value = null;
    try {
      const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
      });
      const json = (await res.json()) as ApiResponse<T>;
      if (json.code !== 0) {
        error.value = json.message;
      }
      return json;
    } catch (e: unknown) {
      const msg: string =
        e instanceof Error ? e.message : '网络请求失败';
      error.value = msg;
      return { code: -1, data: null, message: msg };
    } finally {
      loading.value = false;
    }
  }

  /** GET 请求 */
  function get<T>(url: string): Promise<ApiResponse<T>> {
    return request<T>(url);
  }

  /** POST 请求 */
  function post<T>(url: string, body: unknown): Promise<ApiResponse<T>> {
    return request<T>(url, {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  /** DELETE 请求 */
  function del<T>(url: string): Promise<ApiResponse<T>> {
    return request<T>(url, { method: 'DELETE' });
  }

  return { loading, error, get, post, del };
}
