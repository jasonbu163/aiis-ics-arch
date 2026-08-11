/**
 * 文件路径: /frontend-js/src/app/system/api/index.js
 * 功能描述: 系统模块 API facade，聚合用户和字典管理接口
 * 主要功能:
 *   - 暴露系统管理页面所需 API
 *   - 隐藏模块内 user/dict API 文件拆分
 */

export * from './user'
export * from './dict'
export * from './projectionMapping'
