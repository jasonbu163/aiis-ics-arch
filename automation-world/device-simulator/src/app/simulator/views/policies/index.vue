<!-- 当前配置草稿策略表；PLC/DB筛选与稳定ID跨页选择，副本编辑与保存/运行分离。 -->
<template>
  <section class="console-stack" data-testid="page-policies">
    <ConfigRevisionBar />
    <ConsoleCard title-key="simulator.policies">
      <div class="ds-policy-filter">
        <el-select v-model="local.instanceId" :placeholder="t('simulator.instance')" :aria-label="t('simulator.instance')">
          <el-option v-for="i in local.draft?.instances" :key="i.id" :value="i.id" :label="i.name" />
        </el-select>
        <el-select v-model="dbFilters" multiple clearable :placeholder="t('simulator.editing.allDbs')" :aria-label="t('simulator.editing.dbFilter')">
          <el-option v-for="d in local.selected?.dbs" :key="d.id" :value="d.id" :label="'DB'+d.number+' · '+d.name" />
        </el-select>
      </div>
      <el-alert :title="t('simulator.editing.draftHint')" type="info" :closable="false" />
      <el-alert v-if="message" :title="t('simulator.editing.'+message)" type="warning" :closable="false" />
      <div class="ds-actions">
        <strong>{{ t('simulator.editing.selectedCount',{count:ids.length,total:allRows.length}) }}</strong>
        <ConsoleActionButton label-key="simulator.editing.batch" :disabled="!ids.length||local.busy||local.editing" @click="batchOpen=true" />
        <ConsoleActionButton label-key="simulator.confirmInitialPolicy" :disabled="!ids.length||local.busy||local.editing" @click="local.save(ids)" />
        <ConsoleActionButton label-key="simulator.editing.clearSelection" :disabled="!ids.length" @click="selected=new Set()" />
      </div>
      <ConsoleTableShell v-model:current-page="page" v-model:page-size="pageSize" :page-sizes="[10,20,50]" :total="allRows.length">
        <ConsoleDataTable table-id="configuration.policies" :data="rows" row-key="point.id" class="ds-technical-table" data-testid="policy-table">
          <el-table-column column-key="selection" width="48" :resizable="false" :show-overflow-tooltip="false" fixed="left">
            <template #header><el-checkbox :model-value="!!allRows.length&&ids.length===allRows.length" :indeterminate="ids.length>0&&ids.length<allRows.length" :aria-label="t('simulator.editing.selectAll')" @change="selectAll" /></template>
            <template #default="{row}"><el-checkbox :model-value="selected.has(row.point.id)" :aria-label="row.point.name||row.point.id" @change="toggle(row.point.id)" /></template>
          </el-table-column>
          <el-table-column column-key="db" min-width="180" :label="t('simulator.db')"><template #default="{row}"><span :title="row.db.id">DB{{ row.db.number }} · {{ row.db.name }}</span></template></el-table-column>
          <el-table-column column-key="name" min-width="200" :label="t('simulator.name')"><template #default="{row}"><span :title="row.point.id">{{ row.point.name||row.point.sourcePath }}</span></template></el-table-column>
          <el-table-column column-key="dataType" min-width="110" :label="t('simulator.dataType')"><template #default="{row}">{{ row.point.dataType }}</template></el-table-column>
          <el-table-column column-key="address" min-width="110" :label="t('simulator.address')"><template #default="{row}">{{ row.point.byte??'—' }}{{ row.point.bit===null?'':'.'+row.point.bit }}</template></el-table-column>
          <el-table-column column-key="mode" min-width="130" :label="t('simulator.mode')"><template #default="{row}">{{ display('mode',row.effective.policy.mode) }}<div v-for="code in row.effective.errors" :key="code" class="ds-policy-error">{{ t('simulator.errors.'+code) }}</div></template></el-table-column>
          <el-table-column column-key="initial" min-width="130" :label="t('simulator.initial')"><template #default="{row}">{{ display('initial',row.effective.policy.initial) }}</template></el-table-column>
          <el-table-column column-key="owner" min-width="140" :label="t('simulator.owner')"><template #default="{row}">{{ display('owner',row.effective.policy.owner) }}</template></el-table-column>
          <el-table-column column-key="rule" min-width="240" :label="t('simulator.ruleParameters')"><template #default="{row}">{{ ruleSummary(row.effective.policy) }}</template></el-table-column>
          <el-table-column column-key="confirmation" min-width="200" :show-overflow-tooltip="false" class-name="ds-cell-wrap" :label="t('simulator.confirmation')">
            <template #default="{row}"><div>{{ t('simulator.initial') }}: {{ t(row.point.confirmations.initial?'simulator.confirmed':'simulator.pending') }}</div><div>{{ t('simulator.policies') }}: {{ t(row.point.confirmations.policy?'simulator.confirmed':'simulator.pending') }}</div></template>
          </el-table-column>
          <el-table-column column-key="actions" width="220" :resizable="false" :show-overflow-tooltip="false" fixed="right" :label="t('simulator.action')"><template #default="{row}"><div class="ds-actions">
            <ConsoleActionButton label-key="simulator.editing.editPolicy" size="small" :disabled="local.busy||local.editing" @click="openEditor({level:'point',dbId:row.db.id,id:row.point.id})" />
            <el-popover trigger="click" width="420"><template #reference><ConsoleActionButton label-key="simulator.editing.details" size="small" /></template>
              <strong>{{ row.point.id }}</strong>
              <dl class="ds-facts"><template v-for="field in policyFields" :key="field"><dt>{{ fieldLabel(field) }}</dt><dd class="ds-wrap">{{ display(field,row.effective.policy[field]) }}<small class="ds-policy-source">{{ source(row.effective.sources[field]) }}</small></dd></template></dl>
            </el-popover>
          </div></template></el-table-column>
        </ConsoleDataTable>
      </ConsoleTableShell>
    </ConsoleCard>
    <ConsoleCard title-key="simulator.editing.parentPolicies" compact>
      <div class="ds-policy-selector">
        <el-select v-model="level" :aria-label="t('simulator.editing.parentPolicies')"><el-option v-for="l in ['instance','db','region']" :key="l" :value="l" :label="t('simulator.levels.'+l)" /></el-select>
        <el-select v-if="level!=='instance'" v-model="local.dbId" :placeholder="t('simulator.db')"><el-option v-for="d in local.selected?.dbs" :key="d.id" :value="d.id" :label="'DB'+d.number+' · '+d.name" /></el-select>
        <el-select v-if="level==='region'" v-model="regionId" :placeholder="t('simulator.region')"><el-option v-for="r in local.selectedDb?.regions" :key="r.id" :value="r.id" :label="t('simulator.region')+' '+r.id" /></el-select>
        <ConsoleActionButton label-key="simulator.editing.editPolicy" :disabled="!parentTarget||local.editing||local.busy" @click="openEditor({level,dbId:local.dbId,id:regionId})" />
      </div>
      <div v-if="level==='region'" class="ds-actions">
        <ConsoleActionButton label-key="simulator.addRegion" :disabled="!local.selectedDb||local.editing" @click="addRegion" />
        <el-form-item v-if="region" :label="t('simulator.firstBit')"><el-input-number :model-value="region.firstBit" :min="0" :max="524287" @update:model-value="changeRegion('firstBit',Number($event))" /></el-form-item>
        <el-form-item v-if="region" :label="t('simulator.bitLength')"><el-input-number :model-value="region.bitLength" :min="1" :max="524288" @update:model-value="changeRegion('bitLength',Number($event))" /></el-form-item>
        <ConsoleActionButton v-if="region" label-key="simulator.remove" tone="danger" @click="removeRegion" />
      </div>
      <p>{{ t('simulator.policyHint') }}</p>
    </ConsoleCard>
    <el-dialog v-model="editorOpen" :title="t('simulator.editing.editPolicy')" width="min(920px, calc(100vw - 32px))" :append-to-body="false" :close-on-click-modal="false" @close="cancelEditor">
      <div v-if="editTarget" class="console-stack">
        <PolicyEditor :model-value="editTarget.policy" :data-type="editPoint?.dataType" @update:model-value="editTarget!.policy=$event" @validity="valid=$event" />
        <el-alert v-if="editBaseline!==baseline" :title="t('simulator.editing.staleSelection')" type="error" :closable="false" />
        <ul v-if="editorIssues.length" class="ds-issues"><li v-for="(issue,index) in editorIssues" :key="index">{{ issue }}</li></ul>
        <p>{{ t(editPoint?'simulator.editing.singleEffectivePreview':'simulator.editing.singlePreview') }}</p>
        <div v-for="field in policyFields" :key="field" class="ds-wrap">{{ fieldLabel(field) }}:
          {{ display(field,beforeEffective?beforeEffective.policy[field]:originalPolicy?.[field]) }} <small v-if="beforeEffective">({{ source(beforeEffective.sources[field]) }})</small> →
          {{ display(field,afterEffective?afterEffective.policy[field]:editTarget.policy[field]) }} <small v-if="afterEffective">({{ source(afterEffective.sources[field]) }})</small>
        </div>
      </div>
      <template #footer><ConsoleActionButton label-key="simulator.cancel" @click="cancelEditor" /><ConsoleActionButton label-key="simulator.keepChanges" tone="primary" :disabled="!valid||editBaseline!==baseline||!!editorIssues.length" @click="keepEditor" /></template>
    </el-dialog>
    <PolicyBatchDialog v-if="local.selected" v-model="batchOpen" :instance="local.selected" :ids="ids" :baseline="baseline" @confirm="replaceInstance" />
  </section>
</template>
<script setup lang="ts">
import ConsoleDataTable from '../../../../components/console/ConsoleDataTable.vue';
import { computed, inject, onBeforeUnmount, ref, watch } from 'vue';
import { ElPopover } from 'element-plus';
import { useI18n } from 'vue-i18n';
import type { Instance, Policy } from '../../../../services/deviceSimulator';
import { simulatorKey } from '../../../../console/composables/useDeviceSimulator';
import ConsoleCard from '../../../../components/console/ConsoleCard.vue';
import ConsoleActionButton from '../../../../components/console/ConsoleActionButton.vue';
import ConsoleTableShell from '../../../../components/console/ConsoleTableShell.vue';
import ConfigRevisionBar from '../../../../components/console/ConfigRevisionBar.vue';
import PolicyEditor from '../../components/PolicyEditor.vue';
import PolicyBatchDialog from '../../components/PolicyBatchDialog.vue';
import { clone, draftBaseline, draftRows, effectivePolicy, invalidateConfirmations, policyFields, selectedIds } from '../../policyEditing';
const local=inject(simulatorKey)!, {t}=useI18n();
const dbFilters=ref<string[]>([]), selected=ref(new Set<string>()), page=ref(1), pageSize=ref(10), level=ref('instance'), regionId=ref(''), batchOpen=ref(false), message=ref('');
const allRows=computed(()=>draftRows(local.selected,dbFilters.value));
const rows=computed(()=>allRows.value.slice((page.value-1)*pageSize.value,page.value*pageSize.value).map(row=>({...row,effective:effectivePolicy(local.selected!,row.db,row.point)})));
const ids=computed(()=>selectedIds(allRows.value,selected.value));
const baseline=computed(()=>draftBaseline(local.selected,dbFilters.value,local.configuration?.etag)+'|'+JSON.stringify(ids.value));
const region=computed(()=>local.selectedDb?.regions.find(r=>r.id===regionId.value));
const parentTarget=computed(()=>level.value==='instance'?local.selected:level.value==='db'?local.selectedDb:region.value);
interface Context {level:string;dbId:string;id:string;}
const editorOpen=ref(false), editInstance=ref<Instance|null>(null), context=ref<Context>({level:'point',dbId:'',id:''}), editBaseline=ref(''), valid=ref(true), originalPolicy=ref<Policy|null>(null);
const editDb=computed(()=>editInstance.value?.dbs.find(d=>d.id===context.value.dbId));
const editPoint=computed(()=>context.value.level==='point'?editDb.value?.points.find(p=>p.id===context.value.id):undefined);
const editTarget=computed(()=>context.value.level==='instance'?editInstance.value:context.value.level==='db'?editDb.value:context.value.level==='point'?editPoint.value:editDb.value?.regions.find(r=>r.id===context.value.id));
const beforeEffective=computed(()=>{if(context.value.level!=='point'||!local.selected)return null;const db=local.selected.dbs.find(d=>d.id===context.value.dbId),point=db?.points.find(p=>p.id===context.value.id);return db&&point?effectivePolicy(local.selected,db,point):null;});
const afterEffective=computed(()=>editInstance.value&&editDb.value&&editPoint.value?effectivePolicy(editInstance.value,editDb.value,editPoint.value):null);
const editorIssues=computed(()=>{
    if(!editInstance.value) return [];
    const affected=draftRows(editInstance.value,context.value.level==='instance'?[]:[context.value.dbId]).filter(row=>context.value.level!=='point'||row.point.id===context.value.id);
    return affected.flatMap(row=>effectivePolicy(editInstance.value!,row.db,row.point).errors.map(code=>'DB'+row.db.number+' · '+(row.point.name||row.point.id)+' · '+row.point.dataType+': '+t('simulator.errors.'+code)));
});
function fieldLabel(field:string){return t(field==='rule'?'simulator.ruleParameters':'simulator.'+field);}
function source(value:string){return value.startsWith('region:')?t('simulator.region')+' '+value.slice(7):t('simulator.editing.sources.'+value);}
function display(field:string,value:unknown){return value===null||value===undefined?t('simulator.inherit'):field==='mode'?t('simulator.modes.'+value):field==='owner'?t('simulator.owners.'+value):JSON.stringify(value);}
function ruleSummary(policy:Policy){const r=policy.rule;if(!r)return '—';if(r.kind==='fixed')return t('simulator.fixedValue')+': '+JSON.stringify(r.fixedValue);if(r.kind==='toggle')return t('simulator.halfPeriodMs')+': '+r.halfPeriodMs;return r.min+' … '+r.max+' · '+t('simulator.periodMs')+': '+r.periodMs+(r.kind==='sine'?' · '+t('simulator.phase')+': '+r.phase:r.kind==='random'?' · '+t('simulator.seed')+': '+r.seed:'');}
function toggle(id:string){const next=new Set(selected.value);next.has(id)?next.delete(id):next.add(id);selected.value=next;}
function selectAll(value:unknown){selected.value=value?new Set(allRows.value.map(row=>row.point.id)):new Set();}
function cleanup(){local.editing=false;local.finishEditor=null;local.discardEditor=null;}
function cancelEditor(){editorOpen.value=false;editInstance.value=null;cleanup();}
function resetScope(){if(editorOpen.value||batchOpen.value)message.value='staleSelection';selected.value=new Set();page.value=1;batchOpen.value=false;cancelEditor();}
watch(()=>local.instanceId,()=>{dbFilters.value=[];local.dbId=local.selected?.dbs[0]?.id||'';resetScope();},{flush:'sync'});
watch(dbFilters,resetScope,{deep:true,flush:'sync'});
watch(()=>local.dbId,()=>regionId.value=local.selectedDb?.regions[0]?.id||'',{immediate:true});
watch(()=>allRows.value.length,()=>{page.value=Math.min(page.value,Math.max(1,Math.ceil(allRows.value.length/pageSize.value)));});
function openEditor(value:Context){if(!local.selected)return;context.value=value;editInstance.value=clone(local.selected);editBaseline.value=baseline.value;originalPolicy.value=clone(editTarget.value!.policy);valid.value=true;editorOpen.value=true;local.editing=true;local.finishEditor=keepEditor;local.discardEditor=cancelEditor;}
function replaceInstance(instance:Instance){if(!local.draft)return;const at=local.draft.instances.findIndex(i=>i.id===instance.id);if(at>=0)local.draft.instances.splice(at,1,instance);message.value='keptDraft';}
function keepEditor(){if(!valid.value||editBaseline.value!==baseline.value||editorIssues.value.length||!editInstance.value||!local.selected)return false;invalidateConfirmations(local.selected,editInstance.value);replaceInstance(clone(editInstance.value));cancelEditor();return true;}
function editRegion(mutator:(i:Instance)=>void){if(!local.selected)return;const before=clone(local.selected);mutator(local.selected);invalidateConfirmations(before,local.selected);}
function addRegion(){if(!local.selectedDb)return;const id=crypto.randomUUID();editRegion(()=>local.selectedDb!.regions.push({id,firstBit:0,bitLength:8,policy:{}}));regionId.value=id;}
function removeRegion(){editRegion(()=>{if(local.selectedDb)local.selectedDb.regions=local.selectedDb.regions.filter(r=>r.id!==regionId.value);});regionId.value='';}
function changeRegion(field:'firstBit'|'bitLength',value:number){if(region.value)editRegion(()=>{region.value![field]=value;});}
onBeforeUnmount(cleanup);
</script>
