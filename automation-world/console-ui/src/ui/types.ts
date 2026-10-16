/** 公共 UI 展示类型：不含 Agent 业务模型或应用状态。 */
import type { Component } from 'vue'
export type UiTheme = 'light' | 'dark'
export type UiTone = 'neutral' | 'success' | 'warning' | 'danger'
export type ActionTone = 'primary' | 'secondary' | 'success' | 'warning' | 'danger'
export interface NavigationItem { id: string; label: string; icon?: Component }
