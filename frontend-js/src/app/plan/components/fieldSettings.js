/** 字段管理三种作用域的可编辑设置与实绩归属规则。 */
const basic = ['enabled', 'isNullable']
const plan = ['planEditable', 'planVisible']
const performance = ['performanceEditable', 'performanceVisible']
const performanceOwners = ['automated', 'manual']

export const fieldSettings = {
  shared: {
    owners: ['order_snapshot', 'snapshot_auto', ...performanceOwners],
    switches: [...basic, 'syncEnabled', ...plan, ...performance],
    orders: ['planOrder', 'performanceOrder']
  },
  plan: { owners: [], switches: [...basic, ...plan], orders: ['planOrder'] },
  performance: { owners: performanceOwners, switches: [...basic, ...performance], orders: ['performanceOrder'] }
}

export function settingDisabled(row, key) {
  return (key === 'performanceEditable' && row.performanceOwner !== 'manual')
    || (key === 'syncEnabled' && row.performanceOwner === 'order_snapshot')
}

export function updateFieldOwner(row) {
  if (settingDisabled(row, 'performanceEditable')) row.performanceEditable = false
  if (settingDisabled(row, 'syncEnabled')) row.syncEnabled = false
}
