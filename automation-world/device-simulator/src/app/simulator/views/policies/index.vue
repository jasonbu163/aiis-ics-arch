<!-- 逐属性instance→DB→不重叠region→point；effective及冲突由后端编译/运行快照证明。 -->
<template>
  <section class="console-stack" data-testid="page-policies">
    <ConfigRevisionBar />
    <ConsoleCard title-key="simulator.policies">
      <div class="ds-policy-selector">
        <el-select v-model="local.instanceId" :placeholder="t('simulator.instance')">
          <el-option v-for="i in local.draft?.instances" :key="i.id" :value="i.id" :label="i.name" />
        </el-select>
        <el-select v-model="level" data-testid="policy-level">
          <el-option v-for="l in levels" :key="l" :value="l" :label="t('simulator.levels.'+l)" />
        </el-select>
        <el-select v-if="level!=='instance'" v-model="local.dbId" data-testid="policy-db" :placeholder="t('simulator.db')">
          <el-option v-for="d in local.selected?.dbs" :key="d.id" :value="d.id" :label="d.name" />
        </el-select>
        <el-select v-if="level==='point'" v-model="pointId" data-testid="policy-point">
          <el-option v-for="p in local.selectedDb?.points" :key="p.id" :value="p.id" :label="p.name||p.sourcePath" />
        </el-select>
        <el-select v-if="level==='region'" v-model="regionId">
          <el-option v-for="(r,index) in local.selectedDb?.regions" :key="r.id" :value="r.id" :label="t('simulator.region')+' '+(index+1)" />
        </el-select>
        <ConsoleActionButton v-if="level==='region'" label-key="simulator.addRegion" :disabled="!local.selectedDb" @click="addRegion" />
      </div>
      <div v-if="region&&level==='region'" class="ds-inline">
        <el-form-item :label="t('simulator.firstBit')">
          <el-input-number v-model="region.firstBit" :min="0" :max="524287" />
        </el-form-item>
        <el-form-item :label="t('simulator.bitLength')">
          <el-input-number v-model="region.bitLength" :min="1" :max="524288" />
        </el-form-item>
        <ConsoleActionButton label-key="simulator.remove" tone="danger" @click="removeRegion" />
      </div>
      <PolicyEditor v-if="target" :model-value="target.policy" :data-type="point?.dataType" @update:model-value="target!.policy=$event" />
      <el-empty v-else :image-size="64" :description="t('simulator.selectPolicyTarget')" />
      <p>{{ t('simulator.policyHint') }}</p>
      <ConsoleActionButton v-if="point" label-key="simulator.confirmInitialPolicy" data-testid="policy-confirm" :disabled="local.busy" @click="local.save([point.id])" />
    </ConsoleCard>
  </section>
</template>
<script setup lang="ts">
import { computed, inject, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { simulatorKey } from '../../../../console/composables/useDeviceSimulator';
import ConsoleCard from '../../../../components/console/ConsoleCard.vue';
import ConsoleActionButton from '../../../../components/console/ConsoleActionButton.vue';
import ConfigRevisionBar from '../../../../components/console/ConfigRevisionBar.vue';
import PolicyEditor from '../../components/PolicyEditor.vue';
const local = inject(simulatorKey)!, { t } = useI18n(), levels = ['instance', 'db', 'region', 'point'], level = ref('point'), pointId = ref(''), regionId = ref('');
const point = computed(() => local.selectedDb?.points.find(p => p.id === pointId.value)), region = computed(() => local.selectedDb?.regions.find(r => r.id === regionId.value)), target = computed(() => level.value === 'instance' ? local.selected : level.value === 'db' ? local.selectedDb : level.value === 'point' ? point.value : region.value);
watch(() => local.dbId, () => { pointId.value = local.selectedDb?.points[0]?.id || ''; regionId.value = local.selectedDb?.regions[0]?.id || ''; }, { immediate: true });
function addRegion() { if (!local.selectedDb)
    return; const r = { id: crypto.randomUUID(), firstBit: 0, bitLength: 8, policy: {} }; local.selectedDb.regions.push(r); regionId.value = r.id; }
function removeRegion() { if (local.selectedDb)
    local.selectedDb.regions = local.selectedDb.regions.filter(r => r.id !== regionId.value); regionId.value = ''; }
</script>
