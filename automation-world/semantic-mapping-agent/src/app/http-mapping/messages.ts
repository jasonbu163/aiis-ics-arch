/** HTTP 映射工作台使用本模块自己的双语文案。 */
import { computed, inject, provide, type ComputedRef, type InjectionKey, type Ref } from "vue";
import type { LocaleKey } from "../../locales";
import en from "./locales/en-US.json";
import zh from "./locales/zh-CN.json";

export type HttpMessages = typeof zh;
const english: HttpMessages = en;
const key: InjectionKey<ComputedRef<HttpMessages>> = Symbol("sma HTTP messages");

export function provideHttpMessages(locale: Ref<LocaleKey>) {
  const messages = computed(() => locale.value === "en-US" ? english : zh);
  provide(key, messages);
  return messages;
}

export function useHttpMessages() {
  return inject(key, computed(() => zh));
}

