<!-- CU 私有工作台：共用宿主主题与最近有效方案，同屏组合公共组件和私有样例。 -->
<template>
  <ElConfigProvider :locale="locale === 'zh-CN' ? zhCn : en">
    <AgentLayout :style="previewVariables" :theme="theme" :sidebar-hidden="sidebarHidden">
      <template #sidebar><AgentSidebar :items="navigation" :active-id="section" :brand="t('workbench.brand')" :detail="t('workbench.footer')" @select="section = $event" /></template>
      <template #topbar>
        <AgentTopbar :title="t('workbench.title')" :subtitle="t('workbench.subtitle')" :sidebar-label="t('workbench.sidebar')" :sidebar-hidden="sidebarHidden" @toggle-sidebar="sidebarHidden = !sidebarHidden">
          <template #actions>
            <StatusCapsule :label="t('workbench.sample')" />
            <ThemeToggle :theme="theme" :label="theme === 'light' ? t('workbench.switchToDark') : t('workbench.switchToLight')" @toggle="toggleTheme" />
            <LanguageSwitch :locale="locale === 'zh-CN' ? 'zh-CN' : 'en-US'" :zh-label="t('workbench.zhLabel')" :en-label="t('workbench.enLabel')" :label="locale === 'zh-CN' ? t('workbench.switchToEnglish') : t('workbench.switchToChinese')" @toggle="toggleLocale" />
          </template>
        </AgentTopbar>
      </template>
      <div class="workbench-page">
        <PageSamples v-if="section === 'pages'" :theme="theme" :preview-variables="previewVariables" />
        <div class="workbench-notice"><strong>{{ t('workbench.sample') }}</strong><span>{{ t('workbench.sampleNote') }}</span></div>
        <ConsoleCard v-if="section === 'shell'" :title="t('workbench.shellTitle')" :icon="Monitor">
          <p>{{ t('workbench.shellNote') }}</p>
          <dl class="workbench-facts"><div><dt>{{ t('workbench.contract') }}</dt><dd><code>src/ui/index.ts</code><br /><code>src/ui/styles/index.css</code></dd></div><div><dt>{{ t('workbench.source') }}</dt><dd>{{ t('workbench.sourceNote') }}</dd></div></dl>
          <template #footer>{{ t('workbench.footer') }}</template>
        </ConsoleCard>
        <ConsoleCard v-if="section === 'components'" :title="t('workbench.componentTitle')" :icon="Grid">
          <template #tools><div class="workbench-row"><StatusCapsule v-for="item in tones" :key="item" :tone="item" :label="t(`workbench.${item}`)" /></div></template>
          <div class="workbench-row"><ConsoleActionButton tone="primary" :label="t('workbench.primary')" @click="actionShown = true" /><ConsoleActionButton :label="t('workbench.secondary')" @click="actionShown = true" /><ConsoleActionButton disabled :label="t('workbench.disabled')" /><ConsoleActionButton size="small" :label="t('workbench.reset')" @click="resetPreview" /></div>
          <p v-if="actionShown" class="workbench-feedback" role="status">{{ t('workbench.result') }}</p>
        </ConsoleCard>
        <div v-if="section === 'parameters'" class="design-profile-layout">
          <div class="design-profile-controls">
            <DesignProfileEditor v-model="designProfile" :theme="theme" :preview-variables="previewVariables" :valid-profile="validProfile" @update:theme="setTheme" />
            <details class="design-profile-secondary">
              <summary>{{ t('workbench.designProfile.secondary') }}</summary>
              <ConsoleCard :title="t('workbench.parametersTitle')" :icon="Operation">
                <ElForm label-position="top">
                  <ElFormItem :label="t('workbench.label')"><ElInput v-model="customLabel" :placeholder="t('workbench.defaultLabel')" /></ElFormItem>
                  <ElFormItem :label="t('workbench.tone')"><ElRadioGroup v-model="tone"><ElRadio v-for="item in tones" :key="item" :value="item">{{ t(`workbench.${item}`) }}</ElRadio></ElRadioGroup></ElFormItem>
                  <ElFormItem :label="t('workbench.density')"><ElSwitch v-model="compact" :active-text="t('workbench.enabled')" :inactive-text="t('workbench.disabledValue')" /></ElFormItem>
                </ElForm>
                <ConsoleActionButton :label="t('workbench.reset')" @click="resetPreview" />
              </ConsoleCard>
            </details>
          </div>
          <aside class="design-profile-preview" :aria-label="t('workbench.designProfile.liveTitle')">
            <div class="design-profile-preview-status" role="status" aria-live="polite">
              <strong>{{ t('workbench.designProfile.mode', { mode: t(`workbench.${theme}`) }) }}</strong>
              <p :class="{ 'design-profile-error': previewError }">{{ previewError ? t('workbench.designProfile.unapplied', { field: previewError }) : t('workbench.designProfile.liveNote') }}</p>
            </div>
            <div class="design-profile-preview-content">
              <ConsoleCard :title="customLabel || t('workbench.defaultLabel')" :compact="compact">
                <StatusCapsule :tone="tone" :label="t(`workbench.${tone}`)" /><p class="workbench-preview-note">{{ t('workbench.previewNote') }}</p>
                <div class="aw-form-actions"><ConsoleActionButton tone="primary" :label="t('workbench.primary')" @click="actionShown = true" /><ConsoleActionButton :label="t('workbench.secondary')" @click="actionShown = true" /></div>
                <p v-if="actionShown" class="workbench-feedback" role="status">{{ t('workbench.result') }}</p>
                <template #footer>{{ t('workbench.footer') }}</template>
              </ConsoleCard>
              <PageSamples :theme="theme" :preview-variables="previewVariables" />
            </div>
          </aside>
        </div>
      </div>
    </AgentLayout>
  </ElConfigProvider>
</template>
<script setup lang="ts">
import PageSamples from './PageSamples.vue'
import DesignProfileEditor from './DesignProfileEditor.vue'
import { useSharedDesignProfile } from './useSharedDesignProfile'
import defaults from '../ui/styles/design-profile.json'
import { normalizeProfile, profileVariables } from '../ui/design-profile.js'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElConfigProvider, ElForm, ElFormItem, ElInput, ElRadio, ElRadioGroup, ElSwitch } from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import en from 'element-plus/es/locale/lang/en'
import { Grid, Monitor, Operation } from '@element-plus/icons-vue'
import { AgentLayout, AgentSidebar, AgentTopbar, ConsoleCard, ConsoleActionButton, StatusCapsule, ThemeToggle, LanguageSwitch, type UiTone, type UiTheme } from '../ui'
const { t, locale } = useI18n()
const storedTheme = localStorage.getItem('cu.theme')
const theme = ref<UiTheme>(storedTheme === 'dark' ? 'dark' : 'light')
const sharedDesign = useSharedDesignProfile(defaults)
const designProfile = sharedDesign.profile
const validProfile = ref(normalizeProfile(designProfile.value))
watch(designProfile, value => { try { validProfile.value = normalizeProfile(value) } catch { /* 无效编辑保留上一次有效预览。 */ } }, { deep: true })
const previewError = computed(() => {
  try { normalizeProfile(designProfile.value); return '' }
  catch (error) {
    const path = error instanceof Error ? error.message : 'profile'
    const parts = path.split('.')
    return parts[0] === 'themes' ? `${t(`workbench.${parts[1]}`)} · ${t(`workbench.designProfile.fields.${parts[2]}`)}` : parts[0] === 'shared' ? t(`workbench.designProfile.fields.${parts[1]}`) : path
  }
})
const previewVariables = computed(() => profileVariables(validProfile.value, theme.value))
const sidebarHidden = ref(false)
const section = sharedDesign.section
const tone = ref<UiTone>('success')
const compact = ref(false)
const customLabel = ref('')
const actionShown = ref(false)
const tones: UiTone[] = ['neutral', 'success', 'warning', 'danger']
const navigation = computed(() => [{ id: 'shell', label: t('workbench.shell'), icon: Monitor }, { id: 'components', label: t('workbench.components'), icon: Grid }, { id: 'parameters', label: t('workbench.parameters'), icon: Operation }, { id: 'pages', label: t('workbench.pageSamples.pages'), icon: Grid }])
function setTheme(value: UiTheme) { theme.value = value; localStorage.setItem('cu.theme', value) }
function toggleTheme() { setTheme(theme.value === 'light' ? 'dark' : 'light') }
function toggleLocale() { locale.value = locale.value === 'zh-CN' ? 'en-US' : 'zh-CN'; localStorage.setItem('cu.locale', locale.value) }
function resetPreview() { tone.value = 'success'; compact.value = false; customLabel.value = ''; actionShown.value = false }
</script>
