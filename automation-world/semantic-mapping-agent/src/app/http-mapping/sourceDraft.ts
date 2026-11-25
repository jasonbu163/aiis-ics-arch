/** GET 点位表单保留 JSON 标量输入及可选的定位与元数据路径。 */
import type { HttpPointDefinition, Scalar } from "./types";
import { jsonText, readJsonScalar } from "./ui";

export interface SourcePointDraft {
  pointKey: string;
  name: string;
  dataType: HttpPointDefinition["dataType"];
  path: string;
  selectById: boolean;
  selectorArray: string;
  selectorKey: string;
  selectorValue: string;
  qualityPath: string;
  observedAtPath: string;
  sampleIdPath: string;
  acceptedQuality: string;
}

export function pointDraft(point?: HttpPointDefinition): SourcePointDraft {
  return {
    pointKey: point?.pointKey ?? "",
    name: point?.name ?? "",
    dataType: point?.dataType ?? "string",
    path: point?.path ?? "",
    selectById: Boolean(point?.selector),
    selectorArray: point?.selector?.path ?? "",
    selectorKey: point?.selector?.key ?? "",
    selectorValue: jsonText(point?.selector?.value),
    qualityPath: point?.qualityPath ?? "",
    observedAtPath: point?.observedAtPath ?? "",
    sampleIdPath: point?.sampleIdPath ?? "",
    acceptedQuality: point?.acceptedQuality?.join(", ") ?? "",
  };
}

export function pointDefinition(draft: SourcePointDraft): HttpPointDefinition {
  let value: Scalar | null = null;
  try { if (draft.selectById) value = readJsonScalar(draft.selectorValue); }
  catch { throw new Error(`SMA_HTTP_POINT_SELECTOR_INVALID:${draft.pointKey}`); }
  return {
    pointKey: draft.pointKey.trim(),
    name: draft.name.trim(),
    dataType: draft.dataType,
    path: draft.path.trim(),
    selector: value === null ? null : { path: draft.selectorArray.trim(), key: draft.selectorKey.trim(), value },
    qualityPath: draft.qualityPath.trim() || null,
    observedAtPath: draft.observedAtPath.trim() || null,
    sampleIdPath: draft.sampleIdPath.trim() || null,
    acceptedQuality: draft.acceptedQuality.split(",").map(part => part.trim()).filter(Boolean),
  };
}
