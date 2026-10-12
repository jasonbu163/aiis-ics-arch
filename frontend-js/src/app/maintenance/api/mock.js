/**
 * 文件路径: /frontend-next-js/src/app/maintenance/api/mock.js
 * 功能描述: maintenance 前端 mock 诊断实现
 * 主要功能:
 *   - 在 VITE_FRONTEND_MOCK_ENABLED=true 时提供模块本地诊断数据
 *   - 与 /frontend-next-js/src/app/maintenance/api/index.js 保持同名导出
 */
import {
  MOCK_LABEL,
  createMockMutation,
  createMockPage,
  createMockRecord,
  mockToday
} from '@/api/mock/_diagnostic'

const makeMaintenanceItem = (apiName, index) => createMockRecord(apiName, index, {
  maintenanceCode: `MOCK-MAINT-${String(index).padStart(3, '0')}`,
  maintenanceName: `${MOCK_LABEL}-EQUIPMENT-${index}`,
  equipmentName: `${MOCK_LABEL}-EQUIPMENT-${index}`,
  maintenanceType: 'inspection',
  cycleDays: 30,
  content: `${MOCK_LABEL}-MAINTENANCE-CONTENT`
})

const makeMaintenanceLog = (apiName, index) => createMockRecord(apiName, index, {
  maintenanceId: 900000 + index,
  maintenanceCode: `MOCK-MAINT-${String(index).padStart(3, '0')}`,
  maintenanceName: `${MOCK_LABEL}-EQUIPMENT-${index}`,
  maintenanceType: 'inspection',
  content: `${MOCK_LABEL}-MAINTENANCE-CONTENT`,
  lastDate: mockToday(),
  nextDate: mockToday(),
  cycleDays: 30,
  status: index === 1 ? 'normal' : 'warning',
  operator: MOCK_LABEL
})

export async function getMaintenanceItems(params) {
  const apiName = 'maintenance.getMaintenanceItems'
  return createMockPage(apiName, params, [makeMaintenanceItem(apiName, 1), makeMaintenanceItem(apiName, 2)])
}

export async function getMaintenanceLogList(params) {
  const apiName = 'maintenance.getMaintenanceLogList'
  return createMockPage(apiName, params, [makeMaintenanceLog(apiName, 1), makeMaintenanceLog(apiName, 2)])
}

export async function createMaintenanceLog(data) {
  return createMockMutation('maintenance.createMaintenanceLog', data)
}

export async function updateMaintenanceLog(id, data) {
  return createMockMutation('maintenance.updateMaintenanceLog', data, id)
}

export async function deleteMaintenanceLog(id) {
  return createMockMutation('maintenance.deleteMaintenanceLog', {}, id)
}
