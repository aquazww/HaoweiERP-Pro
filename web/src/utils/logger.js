/**
 * 日志工具
 * 统一管理日志输出，生产环境可禁用调试日志
 */

const isDev = import.meta.env.DEV

/**
 * 调试日志（仅开发环境输出）
 * @param  {...any} args - 日志参数
 */
export const log = (...args) => {
  if (isDev) {
    console.log('[DEBUG]', ...args)
  }
}

/**
 * 警告日志
 * @param  {...any} args - 日志参数
 */
export const warn = (...args) => {
  console.warn('[WARN]', ...args)
}

/**
 * 错误日志
 * @param  {...any} args - 日志参数
 */
export const error = (...args) => {
  console.error('[ERROR]', ...args)
}

/**
 * 信息日志
 * @param  {...any} args - 日志参数
 */
export const info = (...args) => {
  if (isDev) {
    console.info('[INFO]', ...args)
  }
}

export default {
  log,
  warn,
  error,
  info
}
