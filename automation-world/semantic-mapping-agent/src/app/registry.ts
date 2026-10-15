/** SMA manifests preserve generic data/mapping and local help only. */
import { backendConnectionPage, connectionManifest } from "./connection/manifest";
import type { AppModuleManifest, AppPage, WorkspaceLocation, WorkspaceManifest } from "./navigation";
import { twinFactsManifest } from "./twin-facts/manifest";
export const moduleManifests: readonly AppModuleManifest[] = [connectionManifest, twinFactsManifest];
export const pageManifests = moduleManifests.flatMap(m => m.pages);
export const workspaceManifests: readonly WorkspaceManifest[] = [
 { id: "dataWorkspace", labelKey: "navDataWorkspace", order: 10, pages: [backendConnectionPage, ...twinFactsManifest.pages] },
 { id: "helpCenter", labelKey: "helpCenterNav", order: 30, pages: [{ id: "helpQuickStart", labelKey: "helpCenterNav", helpKey: "", defaultDetail: "" }] },
];
export function getWorkspaceLocation(page: AppPage): WorkspaceLocation {
 const owner = workspaceManifests.find(w => w.pages.some(p => p.id === page));
 return { workspaceId: owner?.id ?? "dataWorkspace", page };
}
