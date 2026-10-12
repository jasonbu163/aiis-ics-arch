/**
 * 文件路径: /frontend-js/src/config/systemName.js
 * 功能描述: 将构建期双语系统名称和可选登录描述作为普通文本接入 i18n。
 */
export function withSystemNames(messages, env = {}) {
  const result = { ...messages }
  for (const [locale, suffix] of [['zh-CN', 'ZH_CN'], ['en-US', 'EN_US']]) {
    const name = env[`VITE_SYSTEM_NAME_${suffix}`]?.trim()
    const subtitle = env[`VITE_SYSTEM_SUBTITLE_${suffix}`]?.trim() || ''
    result[locale] = {
      ...messages[locale],
      common: name ? {
        ...messages[locale].common,
        // 消息函数保留 @、{}、| 等普通字符，避免被当作翻译语法解析。
        systemTitle: () => name
      } : messages[locale].common,
      // 即使为空也提供该语言的消息，避免 fallback 补成其他语言描述。
      login: { ...messages[locale].login, subtitle: () => subtitle }
    }
  }
  return result
}
