# S7 Virtual PLC

This tool runs a local Snap7-compatible simulator for read-only development
checks. It consumes an explicitly supplied `plc_points.yaml` and an optional
simulation profile; it never connects to a physical PLC or writes a production
database.

The public baseline keeps `inputs/` and `outputs/` empty. Generate a temporary
profile with `init-profile`, review it, and pass it explicitly to `dry-run` or
`serve`:

```bash
uv run python plc/s7-virtual-plc/main.py init-profile \
  --profile-output /private/tmp/simulation-profile.xlsx
uv run python plc/s7-virtual-plc/main.py dry-run \
  --profile /private/tmp/simulation-profile.xlsx --rack 0 --slot 1
uv run python plc/s7-virtual-plc/main.py serve \
  --profile /private/tmp/simulation-profile.xlsx --rack 0 --slot 1 --port 1102
```

`PLC_SIM_PLC_KEY`, `PLC_SIM_RACK` and `PLC_SIM_SLOT` identify the simulator
contract. The simulator validates the called TSAP before accepting an S7
session. Port `1102` is recommended for local development.

This proves only the simulator's configured contract and read path. It does not
prove a real CPU, site network, connection limits or PLC write safety.
