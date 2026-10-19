<!-- 最小消费者：无 CU App、工作台、私有 locale、IPC 或 Rust 依赖。 -->
<template>
  <ElConfigProvider :locale="locale === 'zh-CN' ? zhCn : en">
  <AgentLayout :theme="theme" :sidebar-hidden="hidden">
    <template #sidebar><AgentSidebar :active-id="navigationActive" :items="navigation" :brand="t('brand')" :detail="t('detail')" @select="selectNavigation" /></template>
    <template #topbar><AgentTopbar :title="t('title')" :subtitle="t('subtitle')" :sidebar-label="t('sidebar')" :sidebar-hidden="hidden" @toggle-sidebar="hidden = !hidden"><template #actions><ThemeToggle :theme="theme" :label="theme === 'light' ? t('switchToDark') : t('switchToLight')" @toggle="theme = theme === 'light' ? 'dark' : 'light'" /><LanguageSwitch :locale="locale === 'zh-CN' ? 'zh-CN' : 'en-US'" :zh-label="t('zhLabel')" :en-label="t('enLabel')" :label="locale === 'zh-CN' ? t('switchToEnglish') : t('switchToChinese')" @toggle="locale = locale === 'en-US' ? 'zh-CN' : 'en-US'" /></template></AgentTopbar></template>
    <ConsoleCard class="consumer-navigation" :title="t('navigationSample.title')">
      <ElRadioGroup v-model="navigationMode" :aria-label="t('navigationSample.mode')">
        <ElRadio value="flat">{{ t('navigationSample.flat') }}</ElRadio><ElRadio value="grouped">{{ t('navigationSample.grouped') }}</ElRadio>
      </ElRadioGroup>
      <p>{{ t('navigationSample.note') }}</p>
      <p role="status">{{ t('navigationSample.current', { label: navigationLabel }) }}</p>
      <p>{{ t('navigationSample.selections', { count: navigationSelections }) }}</p>
      <ConsoleActionButton :label="t('navigationSample.external')" @click="navigationActive = navigationActive === 'panel-b' ? 'panel-a' : 'panel-b'" />
    </ConsoleCard>
    <ConsoleCard :title="t('sample')"><StatusCapsule :label="t('sample')" tone="warning" /><p class="consumer-note">{{ t('note') }}</p><ConsoleActionButton tone="primary" :label="t('button')" @click="clicked = true" /><p v-if="clicked" role="status">{{ t('result') }}</p></ConsoleCard>
    <ConsoleCard class="consumer-sample" :title="t('pageSample.list')">
      <ElTable class="aw-data-table" :data="[sample]" stripe>
        <ElTableColumn :label="t('pageSample.name')"><template #default="{ row }">{{ row.name || t('pageSample.alpha') }}</template></ElTableColumn>
        <ElTableColumn :label="t('pageSample.kind')"><template #default="{ row }">{{ t(`pageSample.${row.kind}`) }}</template></ElTableColumn>
        <ElTableColumn :label="t('pageSample.edit')" width="160"><template #default><ConsoleActionButton size="small" :label="t('pageSample.edit')" @click="Object.assign(draft, { name: sample.name || t('pageSample.alpha'), kind: sample.kind }); dialogOpen = true" /></template></ElTableColumn>
      </ElTable>
      <ElForm ref="formRef" class="aw-sample-form consumer-sample" :model="form" :rules="rules" label-position="top" @submit.prevent="submitPreview">
        <ElFormItem prop="name" :label="t('pageSample.name')"><ElInput v-model="form.name" /></ElFormItem>
        <ElFormItem :label="t('pageSample.kind')"><ElSelect v-model="form.kind" :teleported="false"><ElOption v-for="kind in kinds" :key="kind" :value="kind" :label="t(`pageSample.${kind}`)" /></ElSelect></ElFormItem>
        <div class="aw-form-actions"><ConsoleActionButton tone="primary" :label="t('pageSample.submit')" @click="submitPreview" /></div>
      </ElForm>
      <p v-if="submitted" role="status">{{ t('pageSample.submitted') }}</p>
      <template #footer>{{ t('sample') }}</template>
    </ConsoleCard>
  </AgentLayout>
  <Teleport to="body">
    <div class="aw-ui aw-sample-overlays" :data-aw-theme="theme">
      <ElDialog v-model="dialogOpen" :title="t('pageSample.dialogTitle')" :append-to-body="false" width="min(480px, 90vw)" :close-on-click-modal="false" @closed="editRef?.clearValidate()">
        <p>{{ t('pageSample.dialogNote') }}</p>
        <ElForm ref="editRef" class="aw-sample-form" :model="draft" :rules="rules" label-position="top" @submit.prevent="confirmEdit">
          <ElFormItem prop="name" :label="t('pageSample.name')"><ElInput v-model="draft.name" /></ElFormItem>
          <ElFormItem :label="t('pageSample.kind')"><ElSelect v-model="draft.kind" :teleported="false"><ElOption v-for="kind in kinds" :key="kind" :value="kind" :label="t(`pageSample.${kind}`)" /></ElSelect></ElFormItem>
        </ElForm>
        <template #footer><div class="aw-form-actions"><ConsoleActionButton :label="t('pageSample.cancel')" @click="dialogOpen = false" /><ConsoleActionButton tone="primary" :label="t('pageSample.confirm')" @click="confirmEdit" /></div></template>
      </ElDialog>
    </div>
  </Teleport>
  </ElConfigProvider>
</template>
<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { ElConfigProvider, ElDialog, ElForm, ElFormItem, ElInput, ElOption, ElRadio, ElRadioGroup, ElSelect, ElTable, ElTableColumn, type FormInstance, type FormRules } from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import en from 'element-plus/es/locale/lang/en'
import { useI18n } from 'vue-i18n'
import { AgentLayout, AgentSidebar, AgentTopbar, ConsoleCard, ConsoleActionButton, StatusCapsule, ThemeToggle, LanguageSwitch, type UiTheme, type NavigationChildItem, type NavigationItem } from '@aw-ui'
const { t, locale } = useI18n()
const theme = ref<UiTheme>('light')
const hidden = ref(false)
const navigationMode = ref<'flat' | 'grouped'>('flat')
const navigationActive = ref('panel-a')
const navigationSelections = ref(0)
const navigationLeaves = computed<NavigationChildItem[]>(() => [
  { id: 'overview', label: t('navigationSample.overview') },
  { id: 'panel-a', label: t('navigationSample.alpha') },
  { id: 'panel-b', label: t('navigationSample.beta') }
])
const navigation = computed<NavigationItem[]>(() => navigationMode.value === 'flat' ? navigationLeaves.value : [
  navigationLeaves.value[0], { id: 'panels', label: t('navigationSample.group'), children: navigationLeaves.value.slice(1) }
])
const navigationLabel = computed(() => navigationLeaves.value.find(item => item.id === navigationActive.value)?.label ?? '')
function selectNavigation(id: string) { navigationActive.value = id; navigationSelections.value++ }
const clicked = ref(false)
const kinds = ['standard', 'compact'] as const
const sample = reactive({ name: '', kind: 'standard' })
const form = reactive({ name: '', kind: 'standard' })
const draft = reactive({ name: '', kind: 'standard' })
const dialogOpen = ref(false)
const submitted = ref(false)
const formRef = ref<FormInstance>()
const editRef = ref<FormInstance>()
const rules = computed<FormRules>(() => ({ name: [{ required: true, whitespace: true, min: 2, max: 24, message: t('pageSample.required'), trigger: 'blur' }] }))
watch(locale, () => { formRef.value?.clearValidate(); editRef.value?.clearValidate() })
async function submitPreview() {
  if (!await formRef.value?.validate().catch(() => false)) return
  Object.assign(sample, { name: form.name.trim(), kind: form.kind })
  submitted.value = true
}
async function confirmEdit() {
  if (!await editRef.value?.validate().catch(() => false)) return
  Object.assign(sample, { name: draft.name.trim(), kind: draft.kind })
  dialogOpen.value = false
  submitted.value = true
}
</script>
<style>
/* 消费端拥有全局 reset 与页面布局。 */
html, body, #app { margin: 0; min-height: 100vh; }
.consumer-sample { margin-top: 18px; }
.consumer-navigation { margin-bottom: 18px; }
.consumer-navigation .console-action-button { max-width: 100%; min-height: 40px; height: auto; white-space: normal; }
.consumer-note { margin: 20px 0; line-height: 1.6; }
</style>
