/**
 * Token estimation for context window safety check.
 *
 * Rough estimation: Chinese char ≈ 1.2 tokens, ASCII char ≈ 0.3 tokens.
 * Used before sending a rewrite request to warn users when the total
 * estimated token count approaches the selected API's context limit.
 */

/** Context window limits per provider (in tokens) */
const CONTEXT_LIMITS: Record<string, number> = {
  DeepSeek: 128_000,
  '通义千问': 32_000,
  '豆包': 32_000,
  OpenAI: 128_000,
}

/** Default limit when provider is unknown */
const DEFAULT_LIMIT = 32_000

/** Fixed overhead: system prompt + output reservation */
const SYSTEM_PROMPT_TOKENS = 800
const OUTPUT_TOKENS = 2_000

/** Estimated tokens per reference article (≈ 2000 汉字) */
const DEFAULT_REF_TOKENS = 1_400

/** Estimate token count for a given text */
export function estimateTokens(text: string): number {
  let tokens = 0
  for (const char of text) {
    if (/[\u4e00-\u9fff]/.test(char)) {
      tokens += 1.2
    } else if (/[a-zA-Z0-9]/.test(char)) {
      tokens += 0.3
    } else {
      tokens += 0.5
    }
  }
  return Math.ceil(tokens)
}

export interface TokenRisk {
  /** Estimated total tokens (system + input + references + output) */
  estimated: number
  /** API context window limit */
  limit: number
  /** Usage percentage (0-100+) */
  percentage: number
  /** Risk level */
  level: 'safe' | 'warning' | 'danger'
  /** Human-readable label for the provider's limit */
  limitLabel: string
}

/**
 * Check whether the total estimated tokens pose a risk for the given provider.
 *
 * @param provider  LLM provider label (e.g., "DeepSeek", "通义千问")
 * @param mainText  The main article text
 * @param referenceCount  Number of reference articles to include
 * @param avgReferenceTokens  Estimated tokens per reference (default 1400)
 */
export function checkTokenRisk(
  provider: string,
  mainText: string,
  referenceCount: number,
  avgReferenceTokens: number = DEFAULT_REF_TOKENS,
): TokenRisk {
  const limit = CONTEXT_LIMITS[provider] ?? DEFAULT_LIMIT
  const mainTokens = estimateTokens(mainText)
  const refTokens = referenceCount * avgReferenceTokens
  const total = SYSTEM_PROMPT_TOKENS + mainTokens + refTokens + OUTPUT_TOKENS
  const percentage = Math.round((total / limit) * 100)

  let level: TokenRisk['level']
  if (percentage >= 90) {
    level = 'danger'
  } else if (percentage >= 70) {
    level = 'warning'
  } else {
    level = 'safe'
  }

  const limitK = limit >= 1000 ? `${Math.round(limit / 1000)}K` : `${limit}`

  return {
    estimated: total,
    limit,
    percentage,
    level,
    limitLabel: limitK,
  }
}
