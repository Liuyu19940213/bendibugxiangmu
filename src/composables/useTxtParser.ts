/**
 * useTxtParser — TXT 批量导入解析器
 * 解析规则：按空行切段 → 首行识别《书名》→ 其余行作为文案
 */
import type { BatchModule } from '@/types';

/** 解析结果 */
export interface ParseResult {
  /** 成功解析的模块列表 */
  modules: BatchModule[];
  /** 无法匹配书名的段落数 */
  unmatchedCount: number;
  /** 未匹配段落的文本列表 */
  unmatchedTexts: string[];
}

/** 书名匹配正则：匹配行首的《...》 */
const BOOK_NAME_RE = /^《(.+?)》/;

/** 数字编号前缀：匹配 "1." "12." "1、" 等 */
const NUMBER_PREFIX_RE = /^\d+[.、，,]\s*/;

/** 从首行提取模块名（最长 30 字） */
function extractBookName(firstLine: string): string {
  // 先尝试《书名》格式
  const match = firstLine.match(BOOK_NAME_RE);
  if (match) return match[1];

  // 无《书名》→ 去掉数字编号前缀，取前 30 字作为模块名
  const cleaned = firstLine.replace(NUMBER_PREFIX_RE, '');
  return cleaned.slice(0, 30);
}

export function useTxtParser() {
  /**
   * 解析 TXT 文本为批量模块列表
   *
   * 解析逻辑：
   * 1. 按连续空行（\n\s*\n）切分为段落块
   * 2. 每个段落块的首行识别书名：
   *    - 有《书名》→ 提取书名，其余行为文案
   *    - 无《书名》→ 去掉数字编号，取前30字为模块名，全文为文案（含首行）
   * 3. 空块跳过
   *
   * @param text - 原始 TXT 文本
   * @returns ParseResult 包含模块列表
   */
  function parse(text: string): ParseResult {
    const blocks: string[] = text.split(/\n\s*\n/).filter((b) => b.trim());

    const modules: BatchModule[] = [];
    const unmatchedTexts: string[] = [];

    for (const block of blocks) {
      const lines: string[] = block.trim().split('\n');
      const firstLine: string = lines[0].trim();
      const hasBookTag = BOOK_NAME_RE.test(firstLine);

      if (hasBookTag) {
        // 有《书名》：书名行独立，其余为文案
        const m = firstLine.match(BOOK_NAME_RE)!;
        modules.push({
          id: crypto.randomUUID(),
          bookName: m[1],
          rawText: lines.slice(1).join('\n').trim(),
          enabled: true,
          status: 'idle',
          sortOrder: modules.length,
        });
      } else {
        // 无《书名》：全文为文案，首行提取为模块名
        const bookName = extractBookName(firstLine);
        const rawText = block.trim();
        if (bookName && rawText) {
          modules.push({
            id: crypto.randomUUID(),
            bookName,
            rawText,
            enabled: true,
            status: 'idle',
            sortOrder: modules.length,
          });
        } else {
          unmatchedTexts.push(block.trim());
        }
      }
    }

    return {
      modules,
      unmatchedCount: unmatchedTexts.length,
      unmatchedTexts,
    };
  }

  /**
   * 快速校验文本中是否有未匹配段落
   *
   * @param text - 原始 TXT 文本
   * @returns valid 表示所有段落均成功匹配，unmatchedCount 为未匹配数
   */
  function validate(text: string): {
    valid: boolean;
    unmatchedCount: number;
  } {
    const blocks: string[] = text.split(/\n\s*\n/).filter((b) => b.trim());
    let unmatched: number = 0;
    for (const block of blocks) {
      const firstLine: string = block.trim().split('\n')[0].trim();
      const bookName = extractBookName(firstLine);
      if (!bookName) unmatched += 1;
    }
    return { valid: unmatched === 0, unmatchedCount: unmatched };
  }

  return { parse, validate };
}
