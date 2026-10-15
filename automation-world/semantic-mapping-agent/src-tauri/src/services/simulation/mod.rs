//! File Path: /automation-world/semantic-mapping-agent/src-tauri/src/services/simulation/mod.rs
//! Description: Backend-HTTP collection-fact Simulation service registry.
//! Main Features:
//!   - Exposes the typed single-fact producer runtime without a SQL Repository

pub mod collection;
pub mod generator;
pub mod model;
pub mod state;

pub use state::{CollectionFactSimulationRuntimeState, FactProducerRuntimeState};
