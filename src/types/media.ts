// ===== 素材库相关类型 =====

import type { MediaType, ImageSource, MediaItem, ImageCategory, BgmStyle, CopyGenre } from './';

export type { MediaType, ImageSource, MediaItem, ImageCategory, BgmStyle, CopyGenre };

/** 素材筛选条件 */
export interface MediaFilter {
  type: MediaType | 'all';
  source: ImageSource | 'all';
  /** 按分类筛选 */
  category: ImageCategory | 'all';
  /** BGM 风格筛选 */
  bgmStyle: BgmStyle | 'all';
  /** 文案题材筛选 */
  genre: CopyGenre | 'all';
  /** 按标签筛选（多选且） */
  tags: string[];
  /** 按书名关联筛选 */
  bookName: string | null;
  /** 搜索关键词（匹配名称和标签） */
  keyword: string;
  /** 排序 */
  sortBy: 'name' | 'createdAt' | 'fileSize';
  sortOrder: 'asc' | 'desc';
}

/** 分类信息 */
export interface CategoryInfo {
  id: string;
  name: string;
  count: number;
  children?: CategoryInfo[];
}

/** 图片上传进度 */
export interface ImageUploadProgress {
  fileName: string;
  /** 0-100 */
  progress: number;
  status: 'uploading' | 'processing' | 'done' | 'error';
  error?: string;
}

/** 冷却期配置 */
export interface CooldownConfig {
  /** 冷却天数，默认 30 */
  days: number;
  /** 是否启用冷却期 */
  enabled: boolean;
}
