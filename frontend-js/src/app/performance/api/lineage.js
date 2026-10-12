/**
 * 文件路径: /frontend-next-js/src/app/performance/api/lineage.js
 * 功能描述: 实绩 lineage summary 与 effective weight API facade
 * 主要功能:
 *   - 对接 B17 /performances/{id}/lineage-summary
 *   - 对接 B17 /performances/{id}/effective-weight
 *   - 复用 transform facade envelope 解析以保留 errorCode
 */
import { callApi } from '@/api/mockMode'
import { requestPerformanceTransform } from './transform'
import * as mockApi from './mock/lineage'

export const getPerformanceLineageSummary = (performanceId) => callApi(
  () => mockApi.getPerformanceLineageSummary(performanceId),
  () => requestPerformanceTransform({
    method: 'get',
    url: `/performances/${performanceId}/lineage-summary`
  }),
  'performanceLineage.getPerformanceLineageSummary'
)

export const overridePerformanceEffectiveWeight = (performanceId, data) => callApi(
  () => mockApi.overridePerformanceEffectiveWeight(performanceId, data),
  () => requestPerformanceTransform({
    method: 'post',
    url: `/performances/${performanceId}/effective-weight`,
    data
  }),
  'performanceLineage.overridePerformanceEffectiveWeight'
)
