/** 版本展示只解析真实保存序号；旧版不在当前列表时用短ID，不伪造序号。 */
import type { Revision } from '../services/deviceSimulator';

export function revisionLabel(id: string | null | undefined, revisions: readonly Revision[] = []): string {
    if (!id) return '—';
    const revision = revisions.find(row => row.revisionId === id);
    return revision ? `v${revision.savedSeq}` : `#${id.slice(0, 8)}`;
}
