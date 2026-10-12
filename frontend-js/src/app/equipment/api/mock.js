/**
 * 文件路径: /frontend-next-js/src/app/equipment/api/mock.js
 * 功能描述: equipment 前端 mock 诊断实现
 * 主要功能:
 *   - 在 VITE_FRONTEND_MOCK_ENABLED=true 时提供模块本地诊断数据
 *   - 与 /frontend-next-js/src/app/equipment/api/index.js 保持同名导出
 */
import {
  MOCK_LABEL,
  createMockMutation,
  createMockPage,
  createMockRecord,
  mockNow
} from '@/api/mock/_diagnostic'

const makeEquipment = (apiName, index) => createMockRecord(apiName, index, {
  equipmentCode: `MOCK-EQ-${String(index).padStart(3, '0')}`,
  equipmentName: `${MOCK_LABEL}-EQUIPMENT-${index}`,
  equipmentType: 'frontend_mock',
  location: MOCK_LABEL
})

const makeMaintenanceLog = (apiName, index) => createMockRecord(apiName, index, {
  equipmentId: 900000 + index,
  equipmentName: `${MOCK_LABEL}-EQUIPMENT-${index}`,
  maintenanceType: 'frontend_mock',
  maintenanceDate: mockNow(),
  operator: MOCK_LABEL,
  content: `${MOCK_LABEL}-MAINTENANCE`
})

export async function getEquipmentList(params) {
  const apiName = 'equipment.getEquipmentList'
  return createMockPage(apiName, params, [makeEquipment(apiName, 1), makeEquipment(apiName, 2)])
}

export async function getEquipmentById(id) {
  return makeEquipment('equipment.getEquipmentById', Number(id) || 1)
}

export async function createEquipment(data) {
  return createMockMutation('equipment.createEquipment', data)
}

export async function updateEquipment(id, data) {
  return createMockMutation('equipment.updateEquipment', data, id)
}

export async function deleteEquipment(id) {
  return createMockMutation('equipment.deleteEquipment', {}, id)
}

export async function getMaintenanceLogList(params) {
  const apiName = 'equipment.getMaintenanceLogList'
  return createMockPage(apiName, params, [makeMaintenanceLog(apiName, 1), makeMaintenanceLog(apiName, 2)])
}

export async function getMaintenanceLogById(id) {
  return makeMaintenanceLog('equipment.getMaintenanceLogById', Number(id) || 1)
}

export async function createMaintenanceLog(data) {
  return createMockMutation('equipment.createMaintenanceLog', data)
}

export async function updateMaintenanceLog(id, data) {
  return createMockMutation('equipment.updateMaintenanceLog', data, id)
}

export async function deleteMaintenanceLog(id) {
  return createMockMutation('equipment.deleteMaintenanceLog', {}, id)
}

export async function getDriveData() {
  return {
    ...createMockRecord('equipment.getDriveData', 1),
    processItems: [
      { id: 'tv', value: 999, unit: '', decimals: 0, status: 'warning' },
      { id: 'km', value: 9.99, unit: '', decimals: 2, status: 'danger' },
      { id: 'oxygen', value: 999, unit: 'ppm', decimals: 0, status: 'danger' },
      { id: 'mufflePressure', value: 999, unit: 'Pa', decimals: 0, status: 'warning' },
      { id: 'dewPoint', set: -99, actual: 99, deviation: 198, unit: 'C', decimals: 2, status: 'danger' },
      { id: 'nh3Flow', set: 999, actual: 111, deviation: -888, unit: 'm3/h', decimals: 2, status: 'danger' },
      { id: 'ngFlow', set: 999, actual: 111, deviation: -888, unit: 'm3/h', decimals: 2, status: 'danger' }
    ],
    tensionItems: [
      { id: 'uncoiler', set: 999, actual: 111, deviation: -888, status: 'danger' },
      { id: 'entryLooper', set: 999, actual: 111, deviation: -888, status: 'danger' },
      { id: 'furnace', set: 999, actual: 111, deviation: -888, status: 'danger' },
      { id: 'exitLooper', set: 999, actual: 111, deviation: -888, status: 'danger' },
      { id: 'recoiler', set: 999, actual: 111, deviation: -888, status: 'danger' }
    ]
  }
}

export async function getTemperatureControlData() {
  const apiName = 'equipment.getTemperatureControlData'
  return {
    ...createMockRecord(apiName, 1),
    heatingZones: [1, 2, 3, 4, 5].map((index) => ({
      setTemp: 999,
      actualTemp: 800 + index,
      sourceType: 'frontend_mock'
    })),
    temperatureHistory: ['08:00', '10:00', '12:00'].map((time, index) => ({
      time,
      zone1: 900 + index,
      zone2: 880 + index,
      zone3: 860 + index,
      zone4: 840 + index,
      zone5: 820 + index
    }))
  }
}

export async function getProductionParametersData() {
  const apiName = 'equipment.getProductionParametersData'
  return {
    ...createMockRecord(apiName, 1),
    productionParameters: {
      coilNo: 'MOCK-PRODUCTION-COIL',
      grade: MOCK_LABEL,
      status: 'producing',
      lastUpdate: mockNow(),
      thickness: 99.99,
      width: 9999,
      entryTime: mockNow(),
      totalTime: 999,
      weight: 999,
      speed: 999
    },
    processSteps: [
      { step: 'uncoiling', status: 'completed', time: 'MOCK-1' },
      { step: 'heating', status: 'processing', time: 'MOCK-2' },
      { step: 'cooling', status: 'pending', time: 'MOCK-3' }
    ]
  }
}
