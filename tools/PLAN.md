# Tools Plan

## Current baseline

The tool suite is source-only and public-safe. It keeps deterministic scanners,
converters, review UIs and local simulator code while excluding site inputs and
generated evidence.

## Rules

1. Inputs are explicit and local; no network or production service access.
2. Outputs are disposable and must not be committed as project evidence.
3. Site PLC contracts and workbooks are private deployment material.
4. Tests use temporary or sanitized fixtures.
5. Tool changes do not authorize backend, Control Agent, database or PLC changes.

Future tool enhancements should add a focused task and preserve these boundaries.
