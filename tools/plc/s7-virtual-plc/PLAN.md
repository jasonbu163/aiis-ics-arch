# S7 Virtual PLC Plan

Keep the simulator local, explicit and read-only. The source baseline retains
the thin CLI, profile parser, runtime model and strict TSAP validation. Inputs
and generated profiles belong to the caller's temporary workspace.

Future changes must not turn the simulator into a physical PLC client, database
writer or production control path.
