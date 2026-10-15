/**
 * File Path: /automation-world/semantic-mapping-agent/src/app/errors.ts
 * Description: Shared user-error formatting at the composition boundary.
 * Main Features: Separates localized primary messages from explicit diagnostic detail.
 */
import type { LocaleMessages } from "../locales";

export interface UserErrorPresentation {
  code: string;
  primaryMessage: string;
  diagnosticDetail: string;
}

export function presentUserError(
  labels: LocaleMessages,
  error: unknown,
): UserErrorPresentation {
  const raw = error instanceof Error ? error.message : String(error);
  const normalized = raw.replace(/^Error:\s*/i, "");
  const code = normalized.split(":", 1)[0]?.trim() || "unknown";
  return {
    code,
    primaryMessage: code === "SMA_EXTERNAL_IO_DISABLED" ? labels.externalIoDisabled : labels.userErrorPrimary,
    diagnosticDetail: raw,
  };
}
