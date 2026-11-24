# Control Agent source index

| Entry | Responsibility |
| --- | --- |
| [App.vue](src/App.vue) | Select the editor or the retained console using the native startup mode. |
| [Workspace.vue](src/app/flow-editor/Workspace.vue) | Workbench, flow revisions, draft state, JSON and editor coordination. |
| [FlowCanvas.vue](src/app/flow-editor/FlowCanvas.vue) | Vue Flow nodes, handles, drag and drop, and edge selection. |
| [Params.vue](src/app/flow-editor/Params.vue) | Logical resource, upstream field and typed parameter selection. |
| [PlcResources.vue](src/app/plc-catalog/PlcResources.vue) | Original PLC catalog preview, commit and bindings. |
| [HttpResources.vue](src/app/http-connections/HttpResources.vue) | Local HTTP targets and masked header management. |
| [NodeTester.vue](src/app/node-tests/NodeTester.vue) | Isolated single-node test preview, confirmation and result. |
| [ca_flow.rs (IPC)](src-tauri/src/commands/ca_flow.rs) | Native pick/save dialogs and the editor command surface. |
| [ca_flow.rs (domain)](src-tauri/src/domain/ca_flow.rs) | Flow JSON, semantic SHA-256 and typed DAG validation. |
| [ca_catalog.rs](src-tauri/src/domain/ca_catalog.rs) | Closed DAA/DS point catalog reader. |
| [ca_workspace.rs](src-tauri/src/services/ca_workspace.rs) | Resource binding, immutable revisions and transaction coordination. |
| [ca_node_test.rs](src-tauri/src/services/ca_node_test.rs) | Verify and resolve a selected node, one-shot test transport and audit result. |
| [ca_store.rs](src-tauri/src/infrastructure/ca_store.rs) | Bounded reads, workspace snapshots and no-replace exports. |
| [node_tests.rs](src-tauri/tests/arch_aw009/node_tests.rs) | Original catalog, semantic digest, flow revision and no-network transport tests. |
