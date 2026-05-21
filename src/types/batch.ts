// ===== 批量创作运行时类型 =====

import type { BatchModule, BatchProgress, GlobalConfig } from './';

/** TXT 导入解析结果 */
export interface TxtImportResult {
  /** 成功解析的模块列表 */
  modules: BatchModule[];
  /** 无法匹配书名的段落数 */
  unmatchedCount: number;
  /** 未匹配段落的文本列表 */
  unmatchedTexts: string[];
}

/** 批量运行结果汇总 */
export interface BatchRunResult {
  total: number;
  completed: number;
  failed: number;
  skipped: number;
  /** 失败模块的详情 */
  failures: BatchFailure[];
}

/** 单个模块失败详情 */
export interface BatchFailure {
  moduleId: string;
  bookName: string;
  reason: string;
}
