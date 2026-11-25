/** 在可见页面轮询本地运行状态，防止重叠读取并在离开后停止刷新。 */
import { onMounted, onBeforeUnmount, ref, shallowRef } from "vue";
import { describeError } from "./ui";

export function usePoll<T>(enabled: boolean, read: () => Promise<T>) {
  const data = shallowRef<T | null>(null);
  const busy = ref(false);
  const error = ref("");
  let timer: ReturnType<typeof setInterval> | undefined;
  let pending = false;
  let mounted = false;
  let generation = 0;

  async function refresh(silent = false) {
    if (pending || !enabled || !mounted) return;
    const observed = generation;
    pending = true;
    busy.value = !silent;
    try {
      const value = await read();
      if (mounted && observed === generation) {
        data.value = value;
        error.value = "";
      }
    } catch (caught) {
      if (mounted && observed === generation) error.value = describeError(caught);
    } finally {
      pending = false;
      busy.value = false;
    }
  }

  function publish(value: T) {
    generation++;
    data.value = value;
    error.value = "";
  }

  onMounted(() => {
    if (!enabled) return;
    mounted = true;
    void refresh();
    timer = setInterval(() => void refresh(true), 1500);
  });

  onBeforeUnmount(() => {
    mounted = false;
    clearInterval(timer);
  });

  return { data, busy, error, refresh, publish };
}
