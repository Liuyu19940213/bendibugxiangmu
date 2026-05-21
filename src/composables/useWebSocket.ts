/**
 * useWebSocket — WebSocket 客户端
 * 支持自动重连（指数退避：3s → 6s → 12s → 24s → 上限 30s）
 */
import { ref, onUnmounted } from 'vue';
import type { WsMessage } from '@/types/api';
import { API } from '@/lib/api';

/** 初始重连延迟（毫秒） */
const INITIAL_RECONNECT_DELAY = 3000;
/** 最大重连延迟（毫秒） */
const MAX_RECONNECT_DELAY = 30000;

export function useWebSocket() {
  const connected = ref<boolean>(false);
  const lastMessage = ref<WsMessage | null>(null);

  let ws: WebSocket | null = null;
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  let reconnectDelay: number = INITIAL_RECONNECT_DELAY;
  let shouldReconnect: boolean = true;

  /** 建立 WebSocket 连接 */
  function connect(): void {
    if (ws?.readyState === WebSocket.OPEN) {
      return;
    }
    ws = new WebSocket(API.wsURL);

    ws.onopen = (): void => {
      connected.value = true;
      reconnectDelay = INITIAL_RECONNECT_DELAY;
    };

    ws.onclose = (): void => {
      connected.value = false;
      if (shouldReconnect) {
        reconnectTimer = setTimeout(() => {
          reconnectDelay = Math.min(reconnectDelay * 2, MAX_RECONNECT_DELAY);
          connect();
        }, reconnectDelay);
      }
    };

    ws.onmessage = (event: MessageEvent): void => {
      try {
        lastMessage.value = JSON.parse(event.data as string) as WsMessage;
      } catch {
        /* 忽略格式错误的消息 */
      }
    };

    ws.onerror = (): void => {
      ws?.close();
    };
  }

  /** 发送消息到服务端 */
  function send(msg: object): void {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(msg));
    }
  }

  /** 断开连接并停止重连 */
  function disconnect(): void {
    shouldReconnect = false;
    if (reconnectTimer !== null) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
    ws?.close();
  }

  onUnmounted(disconnect);

  return { connected, lastMessage, connect, send, disconnect };
}
