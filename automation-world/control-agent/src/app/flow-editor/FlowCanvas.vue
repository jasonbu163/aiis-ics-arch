<!-- 真实 Vue Flow：拖入、拖动、选中和拖把手连线。 -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Handle, Position, VueFlow, useVueFlow } from '@vue-flow/core'
import type { Connection, NodeDragEvent } from '@vue-flow/core'
import '@vue-flow/core/dist/style.css'
import { useI18n } from 'vue-i18n'
import type { Document, Edge, FlowNode, Position as FlowPosition } from '../../services/caFlow'
import {canConnect,edgeKey, layoutPosition, paletteKey, ports} from './model'

const props=defineProps<{document:Document; selected:string; edge:string; invalid:string[]}>()
const emit=defineEmits<{
  select:[id:string]; selectEdge:[id:string];
  connect:[edge:Edge]; invalid:[]; move:[id:string,position:FlowPosition]
}>()
const {t}=useI18n()
const {screenToFlowCoordinate,fitView,zoomIn,zoomOut}=useVueFlow('ca-flow-canvas')
const fitOnMount=props.document.flow.nodes.length>1
const nodes=computed(()=>props.document.flow.nodes.map((node,index)=>({
  id:node.id,type:'flow',position:layoutPosition(props.document,node.id,index),data:node,
  selected:props.selected===node.id
})))
const edges=computed(()=>props.document.flow.edges.map(edge=>({
  id:edgeKey(edge),type:'smoothstep',source:edge.from_node_id, target:edge.to_node_id,sourceHandle:edge.from_port,
  label:edge.from_port==='next'?'':t('flow-editor.port.'+edge.from_port),
  selected:edgeKey(edge)===props.edge,
  class:edgeKey(edge)===props.edge?'ca-edge-selected':''
})))
const canvas=ref<HTMLElement>()
function pointAt(x:number,y:number):FlowPosition|undefined{
  const rect=canvas.value?.getBoundingClientRect()
  if(rect&&x>=rect.left&&x<rect.right&&y>=rect.top&&y<rect.bottom)return screenToFlowCoordinate({x,y})
}
defineExpose({pointAt})
function connect(connection:Connection){
  const {source, target, sourceHandle}=connection
  if (!source || !target || !sourceHandle) {emit('invalid');return}
  const edge={from_node_id:source, from_port:sourceHandle, to_node_id:target}
  if (!canConnect(props.document,edge)) {emit('invalid');return}
  emit('connect',edge)
}
const moved=(event:NodeDragEvent)=>emit('move',event.node.id,event.node.position)
const caption=(node:FlowNode)=>{
  if(node.type==='http.request') return node.config.path
  if(node.type==='plc.read'||node.type==='plc.write') return node.config.point_ref || node.id
  if(node.type==='condition.compare') return '=='
  return node.id
}
</script>
<template>
  <section ref="canvas" class="ca-canvas" aria-label="Vue Flow">
    <VueFlow id="ca-flow-canvas" :nodes="nodes" :edges="edges" :delete-key-code="null" :min-zoom=".25"
      :max-zoom="2" :node-drag-threshold="0" :select-nodes-on-drag="false" :fit-view-on-init="fitOnMount"
      @connect="connect" @node-click="emit('select',$event.node.id)" @edge-click="emit('selectEdge',$event.edge.id)"
      @pane-click="emit('select','')" @node-drag-stop="moved">
      <template #node-flow="{ data, id, selected }">
        <div class="ca-graph-node" :class="{selected, invalid:invalid.includes(id)}" :data-node-id="id">
          <Handle type="target" :position="Position.Left" />
          <span class="ca-node-kind">{{ t('flow-editor.node.'+paletteKey(data)) }}</span>
          <span class="ca-node-caption">{{ caption(data) }}</span>
          <Handle v-for="(port,index) in ports(data)" :id="port" :key="port" type="source" :position="Position.Right"
            :style="{top:ports(data).length===2?(index===0?'32%':'70%'):'50%'}" :title="t('flow-editor.port.'+port)" />
        </div>
      </template>
    </VueFlow>
    <div class="ca-canvas-tools">
      <button type="button" :aria-label="t('flow-editor.zoomIn')" @click="zoomIn()">+</button>
      <button type="button" :aria-label="t('flow-editor.zoomOut')" @click="zoomOut()">−</button>
      <button type="button" @click="fitView({padding:.2,maxZoom:1})">{{t('flow-editor.fit')}}</button>
    </div>
  </section>
</template>
