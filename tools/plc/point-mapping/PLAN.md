# PLC Point Mapping Plan

Keep the converter schema-first and deterministic. It may validate names, types,
offsets and groups, but it must not infer a customer contract or connect to a
PLC. Workbooks and generated YAML are caller-owned artifacts.
