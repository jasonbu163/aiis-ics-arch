<!-- 三态批量覆盖；候选全量预校验后一次提交本地草稿，不调用运行值或持久化IPC。 -->
<template>
  <el-dialog :model-value="modelValue" :title="t('simulator.editing.batch')" width="min(1120px, calc(100vw - 32px))" :append-to-body="false" :close-on-click-modal="false" @close="cancel">
    <div class="console-stack">
      <el-alert :title="t('simulator.editing.batchHint', {count: ids.length})" type="info" :closable="false" />
      <div v-for="field in policyFields" :key="field" class="ds-batch-field">
        <label>{{ t(field==='rule'?'simulator.ruleParameters':'simulator.'+field) }}</label>
        <el-select v-model="actions[field]" :aria-label="t(field==='rule'?'simulator.ruleParameters':'simulator.'+field)">
          <el-option v-for="action in ['keep','set','inherit']" :key="action" :value="action" :label="t('simulator.editing.actions.'+action)" />
        </el-select>
        <template v-if="actions[field]==='set'">
          <el-select v-if="field==='mode'||field==='owner'" v-model="values[field]">
            <el-option v-for="value in field==='mode'?modes:owners" :key="value" :value="value" :label="t('simulator.'+(field==='mode'?'modes.':'owners.')+value)" />
          </el-select>
          <el-input v-else-if="field==='initial'" v-model="initial" :aria-label="t('simulator.initial')" />
          <el-select v-else-if="field!=='rule'" v-model="values[field]">
            <el-option :value="true" :label="t('simulator.allow')" /><el-option :value="false" :label="t('simulator.deny')" />
          </el-select>
          <el-select v-else v-model="rule.kind">
            <el-option v-for="mode in modes.filter(v=>v!=='hold')" :key="mode" :value="mode" :label="t('simulator.modes.'+mode)" />
          </el-select>
        </template>
      </div>
      <el-alert v-if="actions.mode==='set'" :title="t('simulator.editing.modeLinkHint')" type="warning" :closable="false" />
      <div v-if="ruleEnabled" class="ds-form-grid">
        <el-form-item v-if="rule.kind==='fixed'" :label="t('simulator.fixedValue')"><el-input v-model="fixedText" /></el-form-item>
        <template v-else-if="rule.kind!=='toggle'">
          <el-form-item :label="t('simulator.minimum')"><el-input-number v-model="rule.min" /></el-form-item>
          <el-form-item :label="t('simulator.maximum')"><el-input-number v-model="rule.max" /></el-form-item>
        </template>
        <el-form-item :label="t('simulator.periodMs')"><el-input-number v-model="rule.periodMs" :min="100" :precision="0" /></el-form-item>
        <el-form-item :label="t('simulator.halfPeriodMs')"><el-input-number v-model="rule.halfPeriodMs" :min="100" :precision="0" /></el-form-item>
        <el-form-item :label="t('simulator.phase')"><el-input-number v-model="rule.phase" /></el-form-item>
        <el-form-item :label="t('simulator.seed')"><el-input v-model="rule.seed" maxlength="100" /></el-form-item>
      </div>
      <el-alert v-if="result.error" :title="t('simulator.editing.'+result.error)" type="error" :closable="false" />
      <el-alert v-if="result.noop" :title="t('simulator.editing.noop')" type="info" :closable="false" />
      <ul v-if="result.issues.length" class="ds-issues">
        <li v-for="(issue,index) in result.issues" :key="index">DB{{ issue.db }} · {{ issue.name }} · {{ issue.pointId }} · {{ issue.type }}: {{ t('simulator.errors.'+issue.code) }}</li>
      </ul>
      <p>{{ t('simulator.editing.impact', {count: result.changes.length}) }}</p>
      <ConsoleDataTable table-id="preview.policy-batch" :data="result.changes" max-height="360" row-key="pointId" class="ds-technical-table">
        <el-table-column column-key="point" min-width="200" :label="t('simulator.name')"><template #default="{row}">DB{{ row.db }} · {{ row.name }}<small class="ds-policy-source">{{ row.pointId }}</small></template></el-table-column>
        <el-table-column :column-key="side" min-width="380" :show-overflow-tooltip="false" class-name="ds-cell-wrap" v-for="side in ['before','after']" :key="side" :label="t('simulator.editing.'+side)">
          <template #default="{row}"><div v-for="field in policyFields" :key="field" class="ds-wrap">{{ t(field==='rule'?'simulator.ruleParameters':'simulator.'+field) }}: {{ display(field,row[side].policy[field]) }} <small>({{ source(row[side].sources[field]) }})</small></div></template>
        </el-table-column>
      </ConsoleDataTable>
      <el-checkbox v-model="acknowledged">{{ t('simulator.editing.acknowledge') }}</el-checkbox>
    </div>
    <template #footer>
      <ConsoleActionButton label-key="simulator.cancel" @click="cancel" />
      <ConsoleActionButton label-key="simulator.keepChanges" tone="primary" :disabled="!result.candidate||result.noop||!acknowledged||local.busy" @click="keep" />
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import ConsoleDataTable from '../../../components/console/ConsoleDataTable.vue';
import { computed, inject, onBeforeUnmount, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import type { Instance, Policy, Rule } from '../../../services/deviceSimulator';
import { simulatorKey } from '../../../console/composables/useDeviceSimulator';
import ConsoleActionButton from '../../../components/console/ConsoleActionButton.vue';
import { batchCandidate, clone, newRule, policyFields, type BatchPatch, type PolicyField } from '../policyEditing';
const props = defineProps<{ modelValue: boolean; instance: Instance; ids: string[]; baseline: string }>();
const emit = defineEmits<{ 'update:modelValue': [value: boolean]; confirm: [instance: Instance] }>();
const { t } = useI18n(), local = inject(simulatorKey)!;
const modes = ['hold','fixed','ramp','sine','random','toggle'], owners = ['none','client','ui','rule'];
const actions = ref(Object.fromEntries(policyFields.map(f=>[f,'keep'])) as Record<PolicyField,'keep'|'set'|'inherit'>);
const values = ref<Policy>({ mode:'hold',owner:'none',clientRead:true,clientWrite:false,uiWrite:false,uiMaintenance:false });
const initial = ref(''), fixedText = ref('0'), rule = ref<Rule>(newRule('fixed')), openedBaseline = ref(''), acknowledged = ref(false);
const ruleEnabled = computed(()=>actions.value.rule==='set'||actions.value.mode==='set'&&values.value.mode!=='hold'&&actions.value.rule==='keep');
watch(()=>[actions.value.mode,values.value.mode], ()=>{ if(actions.value.mode==='set'&&values.value.mode&&values.value.mode!=='hold') { rule.value = newRule(values.value.mode); fixedText.value='0'; } });
const patch = computed<BatchPatch>(()=>{
    const p: BatchPatch = {};
    for(const field of policyFields) p[field]={action:actions.value[field],value:field==='initial'?initial.value:field==='rule'?{...rule.value,fixedValue:fixedText.value}:values.value[field]};
    if(ruleEnabled.value) p.rule={action:'set',value:{...rule.value,fixedValue:fixedText.value}};
    return p;
});
const result = computed(()=>batchCandidate(props.instance,props.ids,patch.value,openedBaseline.value,props.baseline));
watch(patch,()=>acknowledged.value=false,{deep:true});
function source(value:string) { return value.startsWith('region:')?t('simulator.region')+' '+value.slice(7):t('simulator.editing.sources.'+value); }
function display(field:string,value:unknown) { return field==='mode'?t('simulator.modes.'+value):field==='owner'?t('simulator.owners.'+value):JSON.stringify(value); }
function cleanup() { local.editing=false;local.finishEditor=null;local.discardEditor=null; }
function cancel() { cleanup();emit('update:modelValue',false); }
function keep() { if(!result.value.candidate||result.value.noop||!acknowledged.value) return false;emit('confirm',clone(result.value.candidate));cancel();return true; }
watch(()=>props.modelValue,open=>{ if(open){ openedBaseline.value=props.baseline;actions.value=Object.fromEntries(policyFields.map(f=>[f,'keep'])) as typeof actions.value;initial.value='';fixedText.value='0';rule.value=newRule('fixed');acknowledged.value=false;local.editing=true;local.finishEditor=keep;local.discardEditor=cancel; }else cleanup(); });
onBeforeUnmount(cleanup);
</script>
