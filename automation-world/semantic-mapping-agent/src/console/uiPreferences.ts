/** SMA本机主题/语言偏好；无业务调用、不修改其它应用键。 */
import { ref, watch } from "vue";
import type { UiTheme } from "@aw-ui";
import { DEFAULT_LOCALE, type LocaleKey } from "../locales";
export function readUiPreference<T extends string>(key: string, allowed: readonly T[], fallback: T): T {
  try { const value = window.localStorage.getItem(`sma.${key}`); return allowed.includes(value as T) ? value as T : fallback; }
  catch { return fallback; }
}
export function useUiPreferences() {
  const theme = ref<UiTheme>(readUiPreference("theme", ["light", "dark"], "light"));
  const locale = ref<LocaleKey>(readUiPreference("locale", ["zh-CN", "en-US"], DEFAULT_LOCALE));
  const sidebarHidden = ref(false);
  watch(theme, value => { try { window.localStorage.setItem("sma.theme", value); } catch { /* 本机偏好不可用时保留内存值 */ } });
  watch(locale, value => { try { window.localStorage.setItem("sma.locale", value); } catch { /* 本机偏好不可用时保留内存值 */ } });
  return { theme, locale, sidebarHidden };
}
