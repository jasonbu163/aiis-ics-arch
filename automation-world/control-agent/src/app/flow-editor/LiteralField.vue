<!-- 按类型输入常量或测试值。 -->
<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type {Literal} from '../../services/caFlow'
const props=defineProps<{modelValue:Literal; label:string}>()
const emit=defineEmits<{ 'update:modelValue':[value:Literal] }>()
const {t}=useI18n()
function change(event:Event){
  const input=event.target as HTMLInputElement
  const kind=props.modelValue.type
  const value=kind==='boolean'?input.value==='true':kind==='string'?input.value:input.valueAsNumber
  emit('update:modelValue',{type:kind,value})
}
</script>
<template>
  <label>{{label}}
    <select v-if="modelValue.type==='boolean'" :value="String(modelValue.value)" @change="change">
      <option value="true">{{t('flow-editor.port.true')}}</option>
      <option value="false">{{t('flow-editor.port.false')}}</option>
    </select>
    <input v-else :type="modelValue.type==='string'?'text':'number'" :value="modelValue.value" :step="modelValue.type==='int16'?1:'any'"
      :min="modelValue.type==='int16'?-32768:undefined" :max="modelValue.type==='int16'?32767:undefined" @change="change">
  </label>
</template>
