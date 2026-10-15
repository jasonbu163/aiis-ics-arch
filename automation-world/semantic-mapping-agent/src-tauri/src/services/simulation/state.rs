//! File Path: /automation-world/semantic-mapping-agent/src-tauri/src/services/simulation/state.rs
//! Description: Managed state for the sole TSS collection-fact Simulation runtime.
//! Main Features:
//!   - Enforces one active Simulation instance through ManagedRuntimeState
//!   - Contains no cross-runtime producer claim or retired Flow ownership branch

use crate::domain::runtime::ManagedRuntimeState;

#[derive(Clone)]
pub struct CollectionFactSimulationRuntimeState(pub ManagedRuntimeState);

impl Default for CollectionFactSimulationRuntimeState {
    fn default() -> Self {
        Self(ManagedRuntimeState::new("collection_fact_simulation"))
    }
}

// Temporary compatibility export for the shared composition root. It owns no
// runtime state or claims and can be removed when app.rs drops its old manage call.
#[derive(Debug, Clone, Default)]
pub struct FactProducerRuntimeState;
