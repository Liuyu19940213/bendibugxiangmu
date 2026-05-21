// ============================================================
// Pixelle-Video API Client
// 前端调用 FastAPI 后端的统一入口
// ============================================================

export type TaskStatus = "pending" | "running" | "completed" | "failed" | "cancelled";

// --- Narration / 洗稿 ---
export interface NarrationRequest {
  text: string;
  n_scenes?: number;
  min_words?: number;
  max_words?: number;
}

export interface NarrationResponse {
  success: boolean;
  message: string;
  narrations: string[];
}

// --- TTS / 配音 ---
export interface TTSRequest {
  text: string;
  workflow?: string;
  ref_audio?: string;
}

export interface TTSResponse {
  success: boolean;
  message: string;
  audio_path: string;
  duration: number;
}

// --- Image / 配图 ---
export interface ImageRequest {
  prompt: string;
  width?: number;
  height?: number;
  workflow?: string;
}

export interface ImageResponse {
  success: boolean;
  message: string;
  image_path: string;
}

// --- Video / 生成视频 ---
export interface VideoRequest {
  text: string;
  mode?: "generate" | "fixed";
  title?: string;
  n_scenes?: number;
  tts_workflow?: string;
  tts_speed?: number;
  ref_audio?: string;
  min_narration_words?: number;
  max_narration_words?: number;
  min_image_prompt_words?: number;
  max_image_prompt_words?: number;
  media_workflow?: string;
  video_fps?: number;
  frame_template?: string;
  prompt_prefix?: string;
  template_params?: Record<string, unknown>;
  bgm_path?: string;
  bgm_volume?: number;
  image_paths?: string[];
}

export interface VideoResponse {
  success: boolean;
  message: string;
  video_url: string;
  duration: number;
  file_size: number;
}

export interface VideoAsyncResponse {
  success: boolean;
  message: string;
  task_id: string;
}

// --- Task / 任务查询 ---
export interface TaskInfo {
  task_id: string;
  task_type: string;
  status: TaskStatus;
  progress: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  result?: VideoResponse;
  error?: string;
}

// ============================================================
// API Client
// ============================================================

const DEFAULT_BASE = "http://127.0.0.1:8000";

let _baseUrl = DEFAULT_BASE;

export function setBaseUrl(url: string) {
  _baseUrl = url.replace(/\/+$/, "");
}

export function getBaseUrl(): string {
  return _baseUrl;
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
): Promise<T> {
  const url = `${_baseUrl}${path}`;
  const options: RequestInit = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (body !== undefined) {
    options.body = JSON.stringify(body);
  }

  const res = await fetch(url, options);
  if (!res.ok) {
    const detail = await res.text().catch(() => "Unknown error");
    throw new Error(`[${res.status}] ${detail}`);
  }
  return res.json() as Promise<T>;
}

// --- Health ---
export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${_baseUrl}/health`);
    return res.ok;
  } catch {
    return false;
  }
}

// --- Content ---
export async function generateNarration(
  params: NarrationRequest,
): Promise<NarrationResponse> {
  return request<NarrationResponse>("POST", "/api/content/narration", params);
}

// --- TTS ---
export async function synthesizeTTS(
  params: TTSRequest,
): Promise<TTSResponse> {
  return request<TTSResponse>("POST", "/api/tts/synthesize", params);
}

// --- Image ---
export async function generateImage(
  params: ImageRequest,
): Promise<ImageResponse> {
  return request<ImageResponse>("POST", "/api/image/generate", params);
}

// --- Video (async) ---
export async function generateVideoAsync(
  params: VideoRequest,
): Promise<VideoAsyncResponse> {
  return request<VideoAsyncResponse>(
    "POST",
    "/api/video/generate/async",
    params,
  );
}

// --- Task polling ---
export async function getTask(taskId: string): Promise<TaskInfo> {
  return request<TaskInfo>("GET", `/api/tasks/${taskId}`);
}

// --- Audio / Image URL helper ---
export function getFileUrl(filePath: string): string {
  // Strip common prefix if present, build URL
  const clean = filePath.replace(/\\/g, "/");
  const idx = clean.indexOf("output/");
  const relative = idx >= 0 ? clean.slice(idx + 7) : clean.split("/").pop() ?? clean;
  return `${_baseUrl}/api/files/${relative}`;
}

// --- Rewrite / 动态Few-shot洗稿 ---
export interface RewriteRequest {
  text: string;
  book_name?: string;
  reference_count?: number;
  originality?: number;
  target_chars?: string;
  rewrite_mode?: string;
}

export interface RewriteMeta {
  book_name: string;
  date: string;
  originality: number;
  reference_count: number;
  source_hash: string;
  target_chars: string;
  rewrite_mode: string;
}

export interface RewriteResponse {
  success: boolean;
  message: string;
  content: string;
  reference_count: number;
  meta: RewriteMeta;
}

export async function rewriteContent(req: RewriteRequest): Promise<RewriteResponse> {
  return request<RewriteResponse>("POST", "/api/content/rewrite", req);
}

/** 手动将审核通过的洗稿结果加入素材库 */
export async function saveToLibrary(
  bookName: string,
  content: string,
): Promise<{ success: boolean; message: string; saved: boolean }> {
  return request("POST", "/api/content/rewrite/save-to-library", {
    book_name: bookName,
    content,
  });
}

// ── Prompt 管理 ──

export interface RewritePromptFull {
  assembled_flexible: string;
  assembled_rigid: string;
  is_customized: boolean;
}

export interface RewritePromptSaveReq {
  assembled_flexible: string;
  assembled_rigid: string;
}

export async function getRewritePrompt(): Promise<RewritePromptFull> {
  return request<RewritePromptFull>("GET", "/api/prompts/rewrite");
}

export async function updateRewritePrompt(
  data: RewritePromptSaveReq,
): Promise<{ success: boolean; message: string }> {
  return request("PUT", "/api/prompts/rewrite", data);
}

export async function resetRewritePrompt(): Promise<{ success: boolean; message: string }> {
  return request("DELETE", "/api/prompts/rewrite");
}

// ============================================================
// 批量创作 API
// ============================================================

/** 批量任务状态 */
export interface BatchTaskStatus {
  batch_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  total: number;
  completed: number;
  failed: number;
  skipped: number;
  current_book: string | null;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  modules: ModuleTaskStatus[];
  error_message?: string;
}

/** 单个模块任务状态 */
export interface ModuleTaskStatus {
  module_id: string;
  book_name: string;
  status: 'idle' | 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  progress: number;
  error_message?: string;
  result_path?: string;
  started_at?: string;
  completed_at?: string;
}

/** 启动批量任务请求 */
export interface RunBatchRequest {
  modules: {
    id: string;
    book_name: string;
    raw_text: string;
    enabled: boolean;
    config_override?: Record<string, unknown>;
  }[];
  global_config: {
    voice_id: string;
    voice_type: 'clone' | 'tts';
    bgm_path: string;
    bgm_style: '激昂' | '宁静';
    duration_min: number;
    duration_max: number;
    visual_style: string;
    rewrite_params: {
      reference_count: number;
      style: string;
      target_words_min: number;
      target_words_max: number;
    };
  };
}

/** 启动批量任务响应 */
export interface RunBatchResponse {
  success: boolean;
  message: string;
  batch_id: string;
}

/** 未完成任务响应 */
export interface PendingBatchResponse {
  has_pending: boolean;
  batch_id?: string;
  batch_info?: BatchTaskStatus;
}

/**
 * 启动批量运行
 * POST /api/batch/run
 */
export async function runBatch(req: RunBatchRequest): Promise<RunBatchResponse> {
  return request<RunBatchResponse>("POST", "/api/batch/run", req);
}

/**
 * 获取批量任务状态
 * GET /api/batch/:batch_id
 */
export async function getBatchStatus(batchId: string): Promise<BatchTaskStatus> {
  return request<BatchTaskStatus>("GET", `/api/batch/${batchId}`);
}

/**
 * 取消批量任务
 * POST /api/batch/:batch_id/cancel
 */
export async function cancelBatch(batchId: string): Promise<{ success: boolean; message: string }> {
  return request("POST", `/api/batch/${batchId}/cancel`);
}

/**
 * 获取单个模块的执行状态
 * GET /api/batch/:batch_id/modules/:module_id
 */
export async function getBatchModuleStatus(
  batchId: string,
  moduleId: string,
): Promise<ModuleTaskStatus> {
  return request<ModuleTaskStatus>("GET", `/api/batch/${batchId}/modules/${moduleId}`);
}

/**
 * 检查未完成的批量任务
 * GET /api/batch/unfinished/check
 */
export async function getPendingBatch(): Promise<PendingBatchResponse> {
  return request<PendingBatchResponse>("GET", "/api/batch/unfinished/check");
}

// ============================================================
// 运行历史 API
// ============================================================

/** 运行历史列表项 */
export interface BatchHistoryItem {
  batch_id: string;
  created_at: string;
  completed_at: string | null;
  status: string;
  total_modules: number;
  completed_modules: number;
  failed_modules: number;
  global_config: Record<string, unknown> | null;
}

/** 模块溯源元数据 */
export interface ModuleTraceMeta {
  source_hash: string;
  originality: number | null;
  reference_count: number;
  char_count: number;
  rewrite_date: string | null;
  book_name: string;
}

/** 运行历史详情 */
export interface BatchHistoryDetail {
  batch_id: string;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  status: string;
  global_config: Record<string, unknown> | null;
  modules: ModuleTraceMeta[];
}

/**
 * 获取运行历史列表
 * GET /api/batch/history/list
 */
export async function getBatchHistory(): Promise<BatchHistoryItem[]> {
  return request<BatchHistoryItem[]>("GET", "/api/batch/history/list");
}

/**
 * 获取运行历史详情（含溯源）
 * GET /api/batch/history/:batch_id
 */
export async function getBatchHistoryDetail(
  batchId: string,
): Promise<BatchHistoryDetail> {
  return request<BatchHistoryDetail>("GET", `/api/batch/history/${batchId}`);
}

// ============================================================
// 定时任务 API
// ============================================================

export interface ScheduleTime {
  hour: number;
  minute: number;
  weekdays: number[];
}

export interface ScheduleConfig {
  id?: string;
  name: string;
  enabled: boolean;
  schedule_time: ScheduleTime;
  template_id: string | null;
  last_run_at: string | null;
  next_run_at: string | null;
  created_at: string | null;
}

export interface ScheduleListResponse {
  schedules: ScheduleConfig[];
}

export async function getSchedules(): Promise<ScheduleListResponse> {
  return request<ScheduleListResponse>("GET", "/api/schedule/list");
}

export async function createSchedule(
  name: string,
  scheduleTime: ScheduleTime,
  templateId: string | null = null,
): Promise<ScheduleConfig> {
  return request<ScheduleConfig>("POST", "/api/schedule/create", {
    name,
    schedule_time: scheduleTime,
    template_id: templateId,
  });
}

export async function updateSchedule(
  id: string,
  updates: Partial<Omit<ScheduleConfig, 'id'>>,
): Promise<ScheduleConfig> {
  return request<ScheduleConfig>("PUT", `/api/schedule/${id}`, updates);
}

export async function deleteSchedule(id: string): Promise<{ success: boolean }> {
  return request<{ success: boolean }>("DELETE", `/api/schedule/${id}`);
}

// ============================================================
// 情绪节奏 API
// ============================================================

export interface EmotionSegment {
  index: number;
  text: string;
  start_time: number;
  end_time: number;
  emotion: string;
  confidence: number;
  duration: number;
}

export interface EmotionRhythmResult {
  video_name: string;
  total_duration: number;
  segments: EmotionSegment[];
  rhythm_profile: string;
  created_at: string;
}

export interface RhythmUploadResponse {
  success: boolean;
  message: string;
  result: EmotionRhythmResult | null;
  analysis_id: string | null;
}

export async function analyzeRhythm(
  text: string,
  name: string = "",
): Promise<RhythmUploadResponse> {
  return request<RhythmUploadResponse>("POST", "/api/rhythm/analyze", {
    text,
    name,
  });
}

export async function updateRhythmSegment(
  analysisId: string,
  segmentIndex: number,
  emotion: string,
  text: string = "",
): Promise<{ success: boolean; message: string }> {
  return request("POST", "/api/rhythm/update", {
    analysis_id: analysisId,
    segment_index: segmentIndex,
    emotion,
    text,
  });
}

// ============================================================
// 模板资源接口
// ============================================================

export interface TemplateInfo {
  name: string;
  display_name: string;
  size: string;
  width: number;
  height: number;
  orientation: string;
  path: string;
  key: string;
}

export interface TemplateContent {
  template: string;
  html: string;
  width: number;
  height: number;
}

export async function listTemplates(): Promise<TemplateInfo[]> {
  const res = await request<{ templates: TemplateInfo[] }>("GET", "/api/resources/templates");
  return res.templates;
}

export async function getTemplateContent(templateKey: string): Promise<TemplateContent> {
  return request<TemplateContent>("GET", `/api/frame/template/content?template=${encodeURIComponent(templateKey)}`);
}

// ============================================================
// LLM 测试
// ============================================================

export interface LLMTestRequest {
  provider: string;
  api_base: string;
  api_key: string;
  model: string;
}

export interface LLMTestResponse {
  ok: boolean;
  detail: string;
}

export async function testLlmConnection(req: LLMTestRequest): Promise<LLMTestResponse> {
  return request<LLMTestResponse>("POST", "/api/llm/test", req);
}

// ============================================================
// 模型管理 API
// ============================================================

export interface ModelInfo {
  name: string
  key: string
  category: string
  size_mb: number
  downloaded: boolean
  local_path: string
  status: string
  required_by: string[]
}

export interface EnvironmentInfo {
  cuda_available: boolean
  cuda_version: string
  gpu_name: string
  vram_total_mb: number
  vram_free_mb: number
  python_version: string
  torch_version: string
  ffmpeg_available: boolean
}

export interface ModelStatusResponse {
  models: ModelInfo[]
  environment: EnvironmentInfo
}

export interface ModelDownloadResponse {
  success: boolean
  message: string
  model_key: string
}

export async function getModelStatus(): Promise<ModelStatusResponse> {
  return request<ModelStatusResponse>("GET", "/api/models/status")
}

export async function downloadModel(modelKey: string): Promise<ModelDownloadResponse> {
  return request<ModelDownloadResponse>("POST", "/api/models/download", { model_key: modelKey })
}

export async function downloadAllModels(): Promise<{ results: Array<{ key: string; status: string; message: string }> }> {
  return request("POST", "/api/models/download-all")
}

// ============================================================
// 视频转文案 API
// ============================================================

export interface VideoExtractTextRequest {
  model_size: string;
}

export interface VideoExtractTextResponse {
  text: string;
  segments: Array<{ start: number; end: number; text: string }>;
  language: string;
}

export async function extractTextFromVideo(
  videoFile: File,
  modelSize: string = "medium",
): Promise<VideoExtractTextResponse> {
  const formData = new FormData();
  formData.append("video_file", videoFile);
  formData.append("model_size", modelSize);
  const resp = await fetch(`/api/video/extract-text`, {
    method: "POST",
    body: formData,
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: resp.statusText }));
    throw new Error(err.detail || "视频转文案失败");
  }
  return resp.json();
}
