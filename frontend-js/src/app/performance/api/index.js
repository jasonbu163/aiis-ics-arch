/**
 * 文件路径: /frontend-next-js/src/app/performance/api/index.js
 * 功能描述: 实绩模块 API facade，聚合可见实绩页面所需接口
 * 主要功能:
 *   - 暴露实绩、分卷、打印和效率相关 API
 *   - 隐藏模块内 API 文件拆分，供页面统一从 @/app/performance/api 导入
 */

export * from './performance'
export * from './split'
export * from './print'
export * from './efficiency'
export * from './transform'
export * from './lineage'
