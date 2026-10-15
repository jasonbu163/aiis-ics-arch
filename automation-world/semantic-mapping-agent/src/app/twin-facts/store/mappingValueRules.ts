/**
 * File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/store/mappingValueRules.ts
 * Description: Reactive Backend-owned Mapping Value Rule state.
 * Main Features:
 *   - Keeps generic presets and Collection Fact-origin presets separate from fact values
 *   - Loads missing fact-origin presets as local drafts before an individual save or removal
 *   - Preserves immutable keys and origins after the Backend creates a preset
 */
import { ref } from "vue";

import {
  applyMappingValueRuleImportInBackend,
  createMappingValueRuleInBackend,
  deleteMappingValueRuleInBackend,
  listCollectionFactsFromBackend,
  listMappingValueRulesFromBackend,
  previewMappingValueRuleImportInBackend,
  updateMappingValueRuleInBackend,
} from "../api";
import type {
  BackendCollectionFactRecord,
  CollectionFactDataType,
  ConfigurationImportPreview,
  MappingValueRuleConfiguration,
  MappingValueRuleConfigurationInput,
} from "../types";

export interface MappingValueRuleDraft {
  valueRuleKey: string | null;
  name: string;
  dataType: CollectionFactDataType;
  valuesJson: string;
  originSourceKey: string | null;
  originFactName: string | null;
  enabled: boolean;
}

export interface FactOriginDraftIdentity {
  sourceKey: string;
  factName: string;
}

function emptyDraft(): MappingValueRuleDraft {
  return {
    valueRuleKey: "",
    name: "",
    dataType: "string",
    valuesJson: "[]",
    originSourceKey: null,
    originFactName: null,
    enabled: true,
  };
}

function originKey(sourceKey: string, factName: string): string {
  return `${sourceKey}\u0000${factName}`;
}

function cloneDraft(draft: MappingValueRuleDraft): MappingValueRuleDraft {
  return { ...draft };
}

function draftFromConfiguration(rule: MappingValueRuleConfiguration): MappingValueRuleDraft {
  return {
    valueRuleKey: rule.valueRuleKey,
    name: rule.name,
    dataType: rule.dataType,
    valuesJson: JSON.stringify(rule.values, null, 2),
    originSourceKey: rule.originSourceKey,
    originFactName: rule.originFactName,
    enabled: rule.enabled,
  };
}

function draftFromFact(fact: BackendCollectionFactRecord): MappingValueRuleDraft {
  return {
    valueRuleKey: null,
    name: `${fact.sourceKey} / ${fact.name}`,
    dataType: fact.dataType,
    valuesJson: "[]",
    originSourceKey: fact.sourceKey,
    originFactName: fact.name,
    enabled: true,
  };
}

function validateDraft(draft: MappingValueRuleDraft): MappingValueRuleConfigurationInput {
  const name = draft.name.trim();
  const originSourceKey = draft.originSourceKey?.trim() || null;
  const originFactName = draft.originFactName?.trim() || null;
  const valueRuleKey = draft.valueRuleKey?.trim() || null;
  if (!name || Boolean(originSourceKey) !== Boolean(originFactName)) {
    throw new Error("MAPPING_VALUE_RULE_REQUIRED");
  }
  if (!originSourceKey && !valueRuleKey) throw new Error("MAPPING_VALUE_RULE_REQUIRED");
  let values: unknown;
  try {
    values = JSON.parse(draft.valuesJson);
  } catch {
    throw new Error("MAPPING_VALUE_RULE_VALUES_INVALID");
  }
  if (!Array.isArray(values)) throw new Error("MAPPING_VALUE_RULE_VALUES_INVALID");
  return {
    valueRuleKey,
    name,
    dataType: draft.dataType,
    values,
    originSourceKey,
    originFactName,
    enabled: draft.enabled,
  };
}

export function useMappingValueRulesStore() {
  const configurations = ref<MappingValueRuleConfiguration[]>([]);
  const factOriginDrafts = ref<MappingValueRuleDraft[]>([]);
  const draft = ref<MappingValueRuleDraft>(emptyDraft());
  const selectedId = ref<string | null>(null);
  const selectedOriginKey = ref<string | null>(null);
  const busy = ref(false);
  const status = ref<"idle" | "saved" | "deleted">("idle");
  const error = ref("");
  const importPreview = ref<ConfigurationImportPreview | null>(null);
  const importItems = ref<unknown[]>([]);

  async function load() {
    await run(async () => {
      configurations.value = await listMappingValueRulesFromBackend();
    });
  }

  async function loadSavedFacts() {
    await run(async () => {
      const savedOrigins = new Set(configurations.value
        .filter((rule) => rule.originSourceKey && rule.originFactName)
        .map((rule) => originKey(rule.originSourceKey as string, rule.originFactName as string)));
      const localDrafts = new Map(factOriginDrafts.value
        .filter((item) => item.originSourceKey && item.originFactName)
        .map((item) => [originKey(item.originSourceKey as string, item.originFactName as string), item]));
      const nextDrafts = [...localDrafts.values()];
      let pageNumber = 1;
      while (true) {
        const page = await listCollectionFactsFromBackend({ page: pageNumber, pageSize: 100 });
        for (const fact of page.items) {
          const key = originKey(fact.sourceKey, fact.name);
          if (!savedOrigins.has(key) && !localDrafts.has(key)) nextDrafts.push(draftFromFact(fact));
        }
        if (page.items.length < 100) break;
        pageNumber += 1;
      }
      factOriginDrafts.value = nextDrafts.sort((left, right) => (
        `${left.originSourceKey}/${left.originFactName}`.localeCompare(
          `${right.originSourceKey}/${right.originFactName}`,
        )
      ));
    });
  }

  function startCreate() {
    selectedId.value = null;
    selectedOriginKey.value = null;
    draft.value = emptyDraft();
    status.value = "idle";
    error.value = "";
  }

  function open(valueRuleId: string) {
    const rule = configurations.value.find((item) => item.id === valueRuleId);
    if (!rule) return;
    selectedId.value = rule.id;
    selectedOriginKey.value = null;
    draft.value = draftFromConfiguration(rule);
    status.value = "idle";
    error.value = "";
  }

  function openFactOriginDraft(sourceKey: string, factName: string) {
    const key = originKey(sourceKey, factName);
    const pending = factOriginDrafts.value.find((item) => (
      item.originSourceKey && item.originFactName
      && originKey(item.originSourceKey, item.originFactName) === key
    ));
    if (!pending) return;
    selectedId.value = null;
    selectedOriginKey.value = key;
    draft.value = cloneDraft(pending);
    status.value = "idle";
    error.value = "";
  }

  function updateDraft(patch: Partial<MappingValueRuleDraft>) {
    draft.value = { ...draft.value, ...patch };
  }

  async function save() {
    await run(async () => {
      const input = validateDraft(draft.value);
      const saved = selectedId.value
        ? await updateMappingValueRuleInBackend(selectedId.value, input)
        : await createMappingValueRuleInBackend(input);
      selectedId.value = saved.id;
      draft.value = draftFromConfiguration(saved);
      configurations.value = upsert(saved);
      if (selectedOriginKey.value) {
        factOriginDrafts.value = factOriginDrafts.value.filter((item) => (
          !item.originSourceKey || !item.originFactName
          || originKey(item.originSourceKey, item.originFactName) !== selectedOriginKey.value
        ));
        selectedOriginKey.value = null;
      }
      status.value = "saved";
    });
  }

  async function remove(valueRuleId: string) {
    await run(async () => {
      await deleteMappingValueRuleInBackend(valueRuleId);
      configurations.value = configurations.value.filter((item) => item.id !== valueRuleId);
      if (selectedId.value === valueRuleId) startCreate();
      status.value = "deleted";
    });
  }

  function removeFactOriginDraft(sourceKey: string, factName: string) {
    removeFactOriginDrafts([{ sourceKey, factName }]);
  }

  function removeFactOriginDrafts(drafts: FactOriginDraftIdentity[]) {
    const keys = new Set(drafts.map((draft) => originKey(draft.sourceKey, draft.factName)));
    if (!keys.size) return;
    factOriginDrafts.value = factOriginDrafts.value.filter((item) => (
      !item.originSourceKey || !item.originFactName || !keys.has(originKey(item.originSourceKey, item.originFactName))
    ));
    if (selectedOriginKey.value && keys.has(selectedOriginKey.value)) startCreate();
  }

  async function previewImport(items: unknown[]) {
    await run(async () => {
      importPreview.value = await previewMappingValueRuleImportInBackend(items);
      importItems.value = items;
    });
  }

  async function applyImport() {
    await run(async () => {
      if (!importItems.value.length || !importPreview.value || importPreview.value.errors.length) {
        throw new Error("MAPPING_VALUE_RULE_IMPORT_PREVIEW_REQUIRED");
      }
      await applyMappingValueRuleImportInBackend(importItems.value);
      configurations.value = await listMappingValueRulesFromBackend();
      importItems.value = [];
      importPreview.value = null;
      status.value = "saved";
    });
  }

  function clearImport() {
    importItems.value = [];
    importPreview.value = null;
  }

  function upsert(saved: MappingValueRuleConfiguration): MappingValueRuleConfiguration[] {
    return [...configurations.value.filter((item) => item.id !== saved.id), saved]
      .sort((left, right) => left.name.localeCompare(right.name));
  }

  async function run(operation: () => Promise<void>) {
    busy.value = true;
    error.value = "";
    try {
      await operation();
    } catch (caught) {
      error.value = String(caught);
      throw caught;
    } finally {
      busy.value = false;
    }
  }

  return {
    configurations,
    factOriginDrafts,
    draft,
    selectedId,
    selectedOriginKey,
    busy,
    status,
    error,
    importPreview,
    load,
    loadSavedFacts,
    startCreate,
    open,
    openFactOriginDraft,
    updateDraft,
    save,
    remove,
    removeFactOriginDraft,
    removeFactOriginDrafts,
    previewImport,
    applyImport,
    clearImport,
  };
}
