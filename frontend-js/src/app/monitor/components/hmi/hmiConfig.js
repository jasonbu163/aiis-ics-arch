/**
 * 文件路径: /frontend-next-js/src/app/monitor/components/hmi/hmiConfig.js
 * 功能描述: HMI 实时监控页面点位展示配置
 * 主要功能:
 *   - 定义 HMI 画面 tabs、点位 key、单位和小数位
 *   - 将 latest snapshot payload 映射为页面组件可消费结构
 *   - 避免在组件中散落 PLC 点位 key
 */

export const hmiTabs = [
  { name: 'overview', labelKey: 'monitor.realtime.hmi.tabs.overview' },
  { name: 'heating', labelKey: 'monitor.realtime.hmi.tabs.heating' },
  { name: 'motorsA', labelKey: 'monitor.realtime.hmi.tabs.motorsA' },
  { name: 'motorsB', labelKey: 'monitor.realtime.hmi.tabs.motorsB' },
  { name: 'coiler', labelKey: 'monitor.realtime.hmi.tabs.coiler' },
  { name: 'position', labelKey: 'monitor.realtime.hmi.tabs.position' }
]

export const summaryMetrics = [
  { id: 'lineSpeed', labelKey: 'monitor.realtime.metrics.lineSpeed', key: 'LineSpeedAct_mpm', unit: 'm/min', decimals: 1 },
  { id: 'techTension', labelKey: 'monitor.realtime.metrics.techTension', key: 'FurnActTension_Kg', unit: 'kg', decimals: 1 },
  { id: 'smallTension', labelKey: 'monitor.realtime.metrics.smallTension', key: 'ActSmallTension', unit: 'kg', decimals: 1 },
  { id: 'length', labelKey: 'monitor.realtime.metrics.length', key: 'Length', unit: 'm', decimals: 1 },
  { id: 'width', labelKey: 'monitor.realtime.metrics.width', key: 'Width', unit: 'mm', decimals: 1 },
  { id: 'thickness', labelKey: 'monitor.realtime.metrics.thickness', key: 'Thickness', unit: 'mm', decimals: 2 }
]

export const heatingUnits = [
  {
    id: 'drying',
    labelKey: 'monitor.realtime.hmi.heating.units.drying',
    actualKey: 'Z7TemAct',
    setKey: 'Z7TemSet',
    outputKey: 'Actoutput_Z7'
  },
  {
    id: 'clean3',
    labelKey: 'monitor.realtime.hmi.heating.units.clean3',
    actualKey: 'Z3TemAct',
    setKey: 'Z3TemSet',
    outputKey: 'Actoutput_Z3',
    liquidKey: 'RinseSpray3_Liquid'
  },
  {
    id: 'clean2',
    labelKey: 'monitor.realtime.hmi.heating.units.clean2',
    actualKey: 'Z2TemAct',
    setKey: 'Z2TemSet',
    outputKey: 'Actoutput_Z2',
    liquidKey: 'RinseSpray2_Liquid'
  },
  {
    id: 'clean1',
    labelKey: 'monitor.realtime.hmi.heating.units.clean1',
    actualKey: 'Z1TemAct',
    setKey: 'Z1TemSet',
    outputKey: 'Actoutput_Z1',
    liquidKey: 'RinseSpray1_Liquid'
  },
  {
    id: 'alkali3',
    labelKey: 'monitor.realtime.hmi.heating.units.alkali3',
    actualKey: 'Z6TemAct',
    setKey: 'Z6TemSet',
    outputKey: 'Actoutput_Z6',
    liquidKey: 'LyeSpray3_Liquid'
  },
  {
    id: 'alkali2',
    labelKey: 'monitor.realtime.hmi.heating.units.alkali2',
    actualKey: 'Z5TemAct',
    setKey: 'Z5TemSet',
    outputKey: 'Actoutput_Z5',
    liquidKey: 'LyeSpray2_Liquid'
  },
  {
    id: 'alkali1',
    labelKey: 'monitor.realtime.hmi.heating.units.alkali1',
    actualKey: 'Z4TemAct',
    setKey: 'Z4TemSet',
    outputKey: 'Actoutput_Z4',
    liquidKey: 'LyeSpray1_Liquid'
  }
]

export const motorGroupsA = [
  [
    'uncoiler',
    's1_1',
    's1_2',
    's2_1',
    's2_2',
    'recoiler',
    'paperRecoiler'
  ],
  [
    'squeeze1',
    'squeeze2',
    'squeeze3',
    'squeeze4',
    'squeeze5',
    'squeeze6',
    'squeeze7'
  ],
  [
    'squeeze8',
    'squeeze9',
    'squeeze10',
    'support1',
    'support2',
    'support3',
    'support4'
  ]
]

export const motorGroupsB = [
  ['support5', 'support6', 'lift1', 'lift2', 'lift3', 'lift4', 'lift5'],
  ['lift6', 'paperUnwinder1', 'paperUnwinder2']
]

const motorDevices = [...motorGroupsA, ...motorGroupsB].flat()

const buildMotorPointKeys = (device) => ({
  rpmKey: `motor_${device}_rpm`,
  currentKey: `motor_${device}_current`,
  torqueKey: `motor_${device}_torque`,
  stateKey: `motor_${device}_state`
})

export const motorFallbackKeys = Object.fromEntries(
  motorDevices.map((device) => [device, buildMotorPointKeys(device)])
)

Object.assign(motorFallbackKeys, {
  uncoiler: { ...motorFallbackKeys.uncoiler, torqueKey: 'Unc1SetTorq' },
  recoiler: { ...motorFallbackKeys.recoiler, torqueKey: 'RecSetTorq' },
  paperRecoiler: { ...motorFallbackKeys.paperRecoiler, torqueKey: 'RewPaper1_SetTorq' },
  paperUnwinder1: { ...motorFallbackKeys.paperUnwinder1, torqueKey: 'UnwPaper1_SetTorq' },
  paperUnwinder2: { ...motorFallbackKeys.paperUnwinder2, torqueKey: 'UnwPaper2_SetTorq' },
  support1: { ...motorFallbackKeys.support1, stateKey: 'Support1_BrakeOn' },
  support2: { ...motorFallbackKeys.support2, stateKey: 'Support2_BrakeOn' },
  s1_1: { ...motorFallbackKeys.s1_1, stateKey: 'S1_1Bir_BrakeOn' },
  s1_2: { ...motorFallbackKeys.s1_2, stateKey: 'S1_2Bir_BrakeOn' },
  s2_1: { ...motorFallbackKeys.s2_1, stateKey: 'S2_1Bir_BrakeOn' },
  s2_2: { ...motorFallbackKeys.s2_2, stateKey: 'S2_2Bir_BrakeOn' }
})

export const coilerPanels = [
  {
    id: 'uncoiler',
    titleKey: 'monitor.realtime.hmi.coiler.uncoiler',
    fields: [
      { labelKey: 'monitor.realtime.hmi.fields.actualDiameter', key: 'Unc1_Dia', unit: 'mm', decimals: 0 },
      { labelKey: 'monitor.realtime.hmi.fields.setTension', key: 'UncSetTension_Kg', unit: 'kg', decimals: 1 },
      { labelKey: 'monitor.realtime.hmi.fields.setTorque', key: 'Unc1SetTorq', unit: '%', decimals: 1 }
    ]
  },
  {
    id: 'furnace',
    titleKey: 'monitor.realtime.hmi.coiler.furnace',
    fields: [
      { labelKey: 'monitor.realtime.hmi.fields.actualTension', key: 'FurnActTension_Kg', unit: 'kg', decimals: 1 },
      { labelKey: 'monitor.realtime.hmi.fields.smallTension', key: 'ActSmallTension', unit: 'kg', decimals: 1 },
      { labelKey: 'monitor.realtime.hmi.fields.lineSpeed', key: 'LineSpeedAct_mpm', unit: 'm/min', decimals: 1 },
      { labelKey: 'monitor.realtime.hmi.fields.width', key: 'Width', unit: 'mm', decimals: 1 },
      { labelKey: 'monitor.realtime.hmi.fields.thickness', key: 'Thickness', unit: 'mm', decimals: 2 }
    ]
  },
  {
    id: 'recoiler',
    titleKey: 'monitor.realtime.hmi.coiler.recoiler',
    fields: [
      { labelKey: 'monitor.realtime.hmi.fields.actualDiameter', key: 'Rec_Dia', fallbackKey: 'Rec1_Dia', unit: 'mm', decimals: 0 },
      { labelKey: 'monitor.realtime.hmi.fields.setTension', key: 'RecSetTension_Kg', unit: 'kg', decimals: 1 },
      { labelKey: 'monitor.realtime.hmi.fields.setTorque', key: 'RecSetTorq', unit: '%', decimals: 1 }
    ]
  }
]

export const positionGroups = [
  {
    id: 'brush',
    titleKey: 'monitor.realtime.hmi.position.brush',
    items: [
      { labelKey: 'monitor.realtime.hmi.position.items.brush1', key: 'ActPositon1' },
      { labelKey: 'monitor.realtime.hmi.position.items.brush2', key: 'ActPositon2' },
      { labelKey: 'monitor.realtime.hmi.position.items.brush3', key: 'ActPositon3' },
      { labelKey: 'monitor.realtime.hmi.position.items.brush4', key: 'ActPositon4' },
      { labelKey: 'monitor.realtime.hmi.position.items.brush5', key: 'ActPositon5' },
      { labelKey: 'monitor.realtime.hmi.position.items.brush6', key: 'ActPositon6' }
    ]
  },
  {
    id: 'lineState',
    titleKey: 'monitor.realtime.hmi.position.lineState',
    items: [
      { labelKey: 'monitor.realtime.hmi.position.items.reset', key: 'DB47_B52_0_Bool', type: 'state' },
      { labelKey: 'monitor.realtime.hmi.position.items.axisEnable', key: 'DB47_B52_1_Bool', type: 'state' },
      { labelKey: 'monitor.realtime.hmi.position.items.axisFault', key: 'DB47_B52_2_Bool', type: 'state' },
      { labelKey: 'monitor.realtime.hmi.position.items.readyOk', key: 'DB47_B53_0_Bool', type: 'state' },
      { labelKey: 'monitor.realtime.hmi.position.items.running', key: 'DB47_B53_3_Bool', type: 'state' },
      { labelKey: 'monitor.realtime.hmi.position.items.stopped', key: 'DB47_B53_4_Bool', type: 'state' }
    ]
  }
]
