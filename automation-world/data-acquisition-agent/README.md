# AIIS Data Acquisition Agent

[中文](README.zh-CN.md) · [User guide](USER_GUIDE.md) · [Task plan](PLAN.md)

DAA is an independent field acquisition application: it reads PLC or simulator points, saves local samples, then reports them to a configured backend. Collection and reporting are controlled separately. Follow the [user guide](USER_GUIDE.md) for the full procedure, synthetic example, two manual checks and troubleshooting. The [common acquisition-data guide](../../docs/acquisition-data-guide.zh-CN.md) covers backend source registration, third-party submissions and reads.

## Start

From the repository root:

```sh
cd automation-world/data-acquisition-agent
pnpm install --frozen-lockfile
pnpm tauri dev
```

After installation, use `pnpm tauri dev` from the DAA project directory. The ordinary Tauri configuration supplies the S7 driver feature. Collection and reporting start stopped by default; the workbench has separate opt-in switches for the next DAA startup. Saving or activating configuration does not itself connect or start them.

## Configuration authority and startup

Source development reads this app's root `.env`. When needed, the user manually copies `.env.example` only if `.env` is absent; review an existing file without overwriting it. `DAA_PROFILE_DIR` selects the independent storage root: a nonblank process value takes precedence over a nonblank value in the selected `.env`, otherwise the app default is used. Advanced `DAA_ENV_FILE` can explicitly select a readable file; an error does not fall back. Paths are absolute literals, with no `~` or environment-variable expansion. An empty value is not an empty directory. Each app has its own profile; development and builds do not isolate data automatically. Installed-package `.env` discovery and distribution are outside this contract.

The UI and local SQLite own PLC, point, group and storage configuration. Automatic YAML migration, the direct-database writer and old runtime entries are retired; ordinary startup does not read the old YAML. Normal operation needs no additional read permission setting. An explicit advanced process `DAA_PLC_READ_ALLOWED` value of false, blank or invalid denies reads; the old key in the selected `.env` cannot override that restriction.

An existing compatible profile can be reused after checking the actual directory. A new empty profile uses config2/runtime4; cold runtime2/3 remains subject to its original admission checks and supports local collection/history without automatic reporting upgrade. Preserve the original configuration, samples, journals and credentials; stop on an identity, time or schema mismatch rather than editing the store. See the [user guide](USER_GUIDE.md#1-start-and-check-the-profile) and [local store notes](src-tauri/src/infrastructure/local_store/README.md).

## Status and boundaries

The Human Owner accepted [DAA-007 r2](plans/DAA-007-ds-joint-validation-and-time-contract/checklist.md#owner-acceptance-r2) on 2026-10-30, completing Stage B only within that controlled DS joint-test scope. Missing historical checkpoints and unexplained actions remain in the original task. See the [DAA plan](PLAN.md) for the precise DAA-010 sample reporting and DAA-013 multi-PLC identity versions and verification states. This guide does not change DAA-010 r5's independent failure, pending Windows native validation, full Stage C gate or actual environment adoption.

Local samples, reporting queues and reliable receipts remain in the selected profile. Only a reliable receipt matching the sample confirms reporting. Real devices, database migration, deployment and production operation follow their own authorization.
