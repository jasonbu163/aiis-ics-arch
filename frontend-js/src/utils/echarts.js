/**
 * 文件路径: /frontend-js/src/utils/echarts.js
 * 功能描述: ECharts 按需装配入口
 * 主要功能:
 *   - 统一注册当前项目实际使用的图表和组件
 *   - 引入官方 dark 主题
 *   - 避免整包引入 echarts 带来的超大 vendor chunk
 */
import * as echarts from 'echarts/core'
import {
  LineChart,
  BarChart,
  PieChart,
  RadarChart,
} from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  ToolboxComponent,
  DataZoomComponent,
  MarkLineComponent,
  MarkPointComponent,
  RadarComponent,
  DatasetComponent,
  TransformComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

import darkTheme from 'echarts/theme/dark'

const lightTheme = {
  color: ['#5e6ad2', '#7a86f5', '#27a644', '#c084fc', '#d97706', '#2563eb'],
  backgroundColor: 'transparent',
  textStyle: {
    color: '#4e5562',
    fontFamily: '"Inter Variable", "Inter", "PingFang SC", sans-serif',
  },
  title: {
    textStyle: {
      color: '#14171f',
      fontWeight: 590,
    },
    subtextStyle: {
      color: '#707887',
    },
  },
  legend: {
    textStyle: {
      color: '#707887',
    },
  },
  categoryAxis: {
    axisLine: {
      lineStyle: { color: 'rgba(17, 24, 39, 0.08)' },
    },
    axisTick: {
      lineStyle: { color: 'rgba(17, 24, 39, 0.08)' },
    },
    axisLabel: {
      color: '#707887',
    },
    splitLine: {
      lineStyle: { color: 'rgba(17, 24, 39, 0.05)' },
    },
  },
  valueAxis: {
    axisLine: {
      show: false,
      lineStyle: { color: 'rgba(17, 24, 39, 0.08)' },
    },
    axisTick: {
      show: false,
      lineStyle: { color: 'rgba(17, 24, 39, 0.08)' },
    },
    axisLabel: {
      color: '#707887',
    },
    splitLine: {
      lineStyle: { color: 'rgba(17, 24, 39, 0.05)' },
    },
  },
}

const customDarkTheme = {
  ...darkTheme,
  color: ['#7170ff', '#828fff', '#27a644', '#8b8ef6', '#d1a14a', '#4f8cff'],
  backgroundColor: 'transparent',
  textStyle: {
    color: '#cfd4dc',
    fontFamily: '"Inter Variable", "Inter", "PingFang SC", sans-serif',
  },
  title: {
    textStyle: {
      color: '#f7f8f8',
      fontWeight: 590,
    },
    subtextStyle: {
      color: '#8a8f98',
    },
  },
  legend: {
    textStyle: {
      color: '#8a8f98',
    },
  },
  categoryAxis: {
    axisLine: {
      lineStyle: { color: 'rgba(255, 255, 255, 0.08)' },
    },
    axisTick: {
      lineStyle: { color: 'rgba(255, 255, 255, 0.08)' },
    },
    axisLabel: {
      color: '#8a8f98',
    },
    splitLine: {
      lineStyle: { color: 'rgba(255, 255, 255, 0.05)' },
    },
  },
  valueAxis: {
    axisLine: {
      show: false,
      lineStyle: { color: 'rgba(255, 255, 255, 0.08)' },
    },
    axisTick: {
      show: false,
      lineStyle: { color: 'rgba(255, 255, 255, 0.08)' },
    },
    axisLabel: {
      color: '#8a8f98',
    },
    splitLine: {
      lineStyle: { color: 'rgba(255, 255, 255, 0.05)' },
    },
  },
}

echarts.registerTheme('aiis-light', lightTheme)
echarts.registerTheme('aiis-dark', customDarkTheme)

echarts.use([
  LineChart,
  BarChart,
  PieChart,
  RadarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  ToolboxComponent,
  DataZoomComponent,
  MarkLineComponent,
  MarkPointComponent,
  RadarComponent,
  DatasetComponent,
  TransformComponent,
  CanvasRenderer,
])

/**
 * 根据当前主题获取 ECharts 主题名称
 * @param {string} theme - 当前主题 'light' | 'dark'
 * @returns {string} ECharts 主题名称
 */
export function getEChartsTheme(theme) {
  return theme === 'dark' ? 'aiis-dark' : 'aiis-light'
}

export default echarts
