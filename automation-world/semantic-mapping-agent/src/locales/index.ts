/**
 * File Path: /automation-world/semantic-mapping-agent/src/locales/index.ts
 * Description: Root locale assembly for module-owned bilingual messages.
 * Main Features: Merges module help and product content deterministically.
 */
import connectionEn from "../app/connection/locales/en-US.json";
import connectionZh from "../app/connection/locales/zh-CN.json";
import twinFactsEn from "../app/twin-facts/locales/en-US.json";
import twinFactsZh from "../app/twin-facts/locales/zh-CN.json";
import commonEn from "./common/en-US.json";
import commonZh from "./common/zh-CN.json";

const zhCN = {
  ...commonZh,
  ...connectionZh,
  ...twinFactsZh,
};
export type LocaleMessages = typeof zhCN;
const enUS: LocaleMessages = {
  ...commonEn,
  ...connectionEn,
  ...twinFactsEn,
};
const dictionaries = { "zh-CN": zhCN, "en-US": enUS };

export const DEFAULT_LOCALE = "zh-CN";
export type LocaleKey = keyof typeof dictionaries;

export function getMessages(locale: string = DEFAULT_LOCALE): LocaleMessages {
  return dictionaries[locale as LocaleKey] || dictionaries[DEFAULT_LOCALE];
}
