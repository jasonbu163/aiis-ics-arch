# Field Flow Python

[中文](README.zh-CN.md)

Python is for learning, practice and rapid prototypes; FF-002 does not package Python. This independent project implements HTTP GET → strict command → SQLite execution state → standard DB INT, preserving existing functionality/tests. Future production flows need not have dual implementations. Language direction does not establish target-platform, field, long-soak or production readiness.

Complete reproducible steps: [USER_GUIDE](USER_GUIDE.md), including preparation, empty-cwd help, explicit init, manual fixture, separate dry-run/execute lessons, inspect/normal stop, actual methods and teaching01 wiring.

Use existing CPython3.11, uv and its own uv.lock/.venv; every uv command explicitly selects --python 3.11 --no-python-downloads. Current fcntl/Unix dependencies do not establish Windows delivery.

Run defaults to dry_run and does not create schema; state init --synthetic creates only a new private directory. Execute needs its own matching store; inspect is read-only. Preserve unknown state/identities without clearing history, changing IDs or blind retry. App writes use Execution.apply. Only demo01 is registered; no automatic discovery, demo02, POST/auth or BOOL/REAL.

Copy this directory independently with its own source, manifest/lock, config, locale, fixture and state; no parent/sibling runtime is required. Parent task links below are optional governance navigation.

The exact dual-version [FF-001 r4](../plans/FF-001-dual-runtime-demo01/spec.md) handoff passed independent [QA2](../plans/FF-001-dual-runtime-demo01/checklist.md); Human Owner final acceptance, field and long-soak remain pending. Earlier failures/evidence are preserved. [FF-002](../plans/FF-002-user-guide-and-runtime-positioning/spec.md) guides have their own DEV/QA/Owner chain, without inheriting FF-001 acceptance.

[PLAN](PLAN.md) · [CODE_INDEX](CODE_INDEX.md) · [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES.md)
