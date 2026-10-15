/** File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/manifest.ts
 * Description: Side-effect-free twin-facts page manifest.
 * Main Features: Declares the Facts & Simulation, Service Mapping, and Mapping Runtime workspaces.
 */
import type { AppModuleManifest } from "../navigation";

export const twinFactsManifest: AppModuleManifest = {
  id: "twin-facts",
  order: 40,
  pages: [
    {
      id: "twinFacts", labelKey: "factsAndSimulationWorkspace", helpKey: "helpTwinFacts", helpTopicId: "collection-facts", defaultDetail: "collection_facts",
      views: [
        { id: "contract", labelKey: "factsTableTitle" },
        { id: "inspector", labelKey: "collectionSimulationTitle" },
      ],
    },
    {
      id: "mappingIdentity", labelKey: "navMappingIdentity", helpKey: "helpMappingTargets", helpTopicId: "service-mapping", defaultDetail: "service-input-mapping.v1",
      views: [
        { id: "apiMaterials", labelKey: "apiMaterialsTitle" },
        { id: "targetApis", labelKey: "targetApiConfigurationTitle" },
        { id: "valueRules", labelKey: "mappingValueRulesTitle" },
        { id: "mappings", labelKey: "mappingConfigurationsTitle" },
      ],
    },
    {
      id: "simulationRuntime", labelKey: "mappingRuntimeWorkspace", helpKey: "helpSimulationRuntime", helpTopicId: "single-fact-runtime", defaultDetail: "HTTP Facts → Target API",
      views: [
        { id: "simulation", labelKey: "mappingExecutionTitle" },
      ],
    },
  ],
};
