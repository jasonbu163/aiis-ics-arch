/** File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/manifest.ts
 * Description: Side-effect-free twin-facts page manifest.
 * Main Features: Declares the Read-only Source Facts, Service Mapping, and Mapping Runtime workspaces.
 */
import type { AppModuleManifest } from "../navigation";

export const twinFactsManifest: AppModuleManifest = {
  id: "twin-facts",
  order: 40,
  pages: [
    {
      id: "twinFacts", labelKey: "sourceFactsWorkspace", defaultDetail: "collection_facts",
      views: [
        { id: "contract", labelKey: "factsTableTitle" },
      ],
    },
    {
      id: "mappingIdentity", labelKey: "navMappingIdentity", defaultDetail: "service-input-mapping.v1",
      views: [
        { id: "apiMaterials", labelKey: "apiMaterialsTitle" },
        { id: "targetApis", labelKey: "targetApiConfigurationTitle" },
        { id: "valueRules", labelKey: "mappingValueRulesTitle" },
        { id: "mappings", labelKey: "mappingConfigurationsTitle" },
      ],
    },
    {
      id: "mappingRuntime", labelKey: "mappingRuntimeWorkspace", defaultDetail: "HTTP Facts → Target API",
      views: [
        { id: "execution", labelKey: "mappingExecutionTitle" },
      ],
    },
  ],
};
