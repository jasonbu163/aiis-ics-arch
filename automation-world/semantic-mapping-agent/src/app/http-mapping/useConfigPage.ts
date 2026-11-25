/** HTTP 配置列表共用 SQLite revision 及显式删除确认。 */
import { computed, ref } from "vue";
import { changeConfiguration, loadLocalConfiguration, localConfiguration } from "../twin-facts/api/localConfiguration";
import { useHttpMessages } from "./messages";
import { describeError } from "./ui";

type Resource = "httpSources" | "targetApis" | "mappingValueRules" | "mappings";
export interface DeleteCandidate { id: string; name: string }

export function useConfigPage(resource: Resource) {
  const ui = useHttpMessages();
  const document = computed(() => localConfiguration.value?.document);
  const ready = computed(() => Boolean(document.value));
  const working = ref(false);
  const notice = ref<"saved" | "deleted" | "">("");
  const error = ref("");
  const deleteOpen = ref(false);
  const deleteName = ref("");
  let deletion: { id: string; revision: number } | undefined;

  function revision() {
    return localConfiguration.value?.revision ?? 0;
  }

  function report(caught: unknown) { error.value = describeError(caught); }

  const errorMessage = computed(() => {
    if (!error.value) return "";
    const explanation = error.value.includes("CONFLICT") ? ui.value.conflict : ui.value.invalid;
    return `${explanation} (${error.value})`;
  });

  async function perform(operation: () => Promise<unknown>, success: typeof notice.value = "") {
    if (working.value) return false;
    working.value = true;
    error.value = "";
    notice.value = "";
    try {
      await operation();
      notice.value = success;
      return true;
    } catch (caught) {
      report(caught);
      return false;
    } finally {
      working.value = false;
    }
  }

  function askDelete(item: DeleteCandidate) {
    deletion = { id: item.id, revision: revision() };
    deleteName.value = item.name;
    error.value = "";
    deleteOpen.value = true;
  }

  async function remove() {
    const item = deletion;
    if (!deleteOpen.value || !item) return;
    if (await perform(() => changeConfiguration({ kind: "delete", resource, id: item.id, payload: null }, item.revision), "deleted")) {
      deleteOpen.value = false;
      deletion = undefined;
    }
  }

  return {
    document, ready, working, notice, error, errorMessage, revision, report, deleteOpen, deleteName, askDelete, remove,
    reload: () => perform(loadLocalConfiguration),
    save: (id: string | null, payload: unknown, expectedRevision: number) =>
      perform(() => changeConfiguration({ kind: "upsert", resource, id, payload }, expectedRevision), "saved"),
  };
}
