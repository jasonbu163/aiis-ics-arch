/**
 * File Path: /automation-world/semantic-mapping-agent/src/app/navigation.ts
 * Description: Shell-level navigation contracts for module manifests.
 * Main Features: Defines stable page IDs without importing module runtime code.
 */
export type AppPage =
  | "backendConnection"
  | "twinFacts"
  | "mappingIdentity"
  | "simulationRuntime"
  | "helpQuickStart"
  | "helpGlossary";

export type WorkspaceId =
  | "dataWorkspace"
  | "helpCenter";

export interface ModulePageManifest {
  id: AppPage;
  labelKey: string;
  helpKey: string;
  helpTopicId?: string;
  defaultDetail: string;
  views?: readonly ModuleViewManifest[];
}

export interface ModuleViewManifest {
  id: string;
  labelKey: string;
}

export interface AppModuleManifest {
  id: string;
  order: number;
  pages: readonly ModulePageManifest[];
}

export interface WorkspaceManifest {
  id: WorkspaceId;
  labelKey: string;
  order: number;
  pages: readonly ModulePageManifest[];
}

export interface WorkspaceLocation {
  workspaceId: WorkspaceId;
  page: AppPage;
}
