// ===== API 通信相关类型 =====

/** SSE 流式事件 */
export interface SseEvent {
  type: 'token' | 'progress' | 'done' | 'error';
  data: string;
}

/** WebSocket 消息 */
export interface WsMessage {
  type: 'progress' | 'log' | 'error' | 'complete';
  payload: WsPayload;
}

/** WebSocket 消息负载联合类型 */
export type WsPayload =
  | { type: 'progress'; moduleId: string; bookName: string; percent: number }
  | { type: 'log'; level: 'info' | 'warn' | 'error'; message: string }
  | { type: 'error'; moduleId: string; message: string }
  | { type: 'complete'; result: import('./batch').BatchRunResult };

/** API 错误码 */
export type ApiErrorCode =
  | 1001   // LLM 调用失败
  | 1002   // TTS 调用失败
  | 1003   // 素材未找到
  | 2001   // 参数校验失败
  | 3001   // Python 服务未启动
  | 3002;  // 文件操作失败
