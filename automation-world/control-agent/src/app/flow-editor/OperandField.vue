<!-- 上游字段选择器与类型化常量。 -->
<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type {Kind, Operand} from '../../services/caFlow'
import {literal,type Output} from './model'
import LiteralField from './LiteralField.vue'
const props=defineProps<{modelValue:Operand; options:Output[]; type?:Kind}>()
const emit=defineEmits<{'update:modelValue':[value:Operand]}>()
const {t}=useI18n()
const allowed=computed(()=>props.options.filter(option=>!props.type || option.type===props.type))
const selection=computed(()=>'node_id' in props.modelValue?props.modelValue.node_id+'.'+props.modelValue.field:'@'+props.modelValue.type)
function pick(event:Event){
  const value=(event.target as HTMLSelectElement).value
  if(value.startsWith('@')) {emit('update:modelValue',literal(value.slice(1) as Kind));return}
  const match=allowed.value.find(option=>option.id+'.'+option.field===value)
  if(match) emit('update:modelValue',{node_id:match.id,field:match.field})
}
</script>
<template>
  <label>{{t('flow-editor.inputSource')}}
    <select :value="selection" @change="pick">
      <option v-if="selection[0]!=='@'&&!allowed.some(x=>x.id+'.'+x.field===selection)" :value="selection" disabled>{{selection}}</option>
      <option v-for="kind in (type?[type]:['int16','real','boolean','string'])" :key="kind" :value="'@'+kind">
        {{t('flow-editor.constant')}} · {{kind}}
      </option>
      <option v-for="x in allowed" :key="x.id+'.'+x.field" :value="x.id+'.'+x.field">
        {{t('flow-editor.node.'+x.kind)}} · {{x.id}}.{{x.field}} · {{x.type}}
      </option>
    </select>
  </label>
  <small v-if="!allowed.length">{{t('flow-editor.noUpstream')}}</small>
  <LiteralField v-if="'type' in modelValue" :model-value="modelValue" :label="t('flow-editor.value')" @update:model-value="emit('update:modelValue',$event)" />
</template>
