/** DS导航及公共CU内容类型：沿DAA适用合同，无采集/上传字段。 */
import type { Component } from 'vue'
export type ConsoleSectionId='overview'|'instances'|'points'|'policies'|'values'|'logs'
export interface ConsoleSectionManifest{id:ConsoleSectionId;titleKey:string;icon:Component;order:number;component:Component}
export interface MetricItem{key:string;labelKey:string;value:string}
export interface OperationItem{key:string;labelKey:string;stateText:string;detailText:string;tone:'ready'|'observing'|'locked'|'blocked'}
