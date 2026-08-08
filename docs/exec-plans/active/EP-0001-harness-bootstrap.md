# EP-0001 Harness Bootstrap

## Objective

Establish the minimum executable development harness.

## Scope

- Normalize docs directory
- Implement tools.py
- Add project definition
- Add quality gate
- Add architecture checker skeleton
- Add initial CI workflow

## Acceptance Criteria

- `python tools.py doctor` executes
- `python tools.py check` executes
- Missing external tools are reported
- No command reports a false PASS
- AGENTS.md links resolve
- CI invokes the same local commands

## Verification Evidence

- Local environment check: `python tools.py doctor`; evidence is written to
  `reports/latest/doctor.{json,md}`.
- Repository contract check: `python tools.py check`; evidence is written to
  `reports/latest/check.{json,md}`.
- Firmware build: `python tools.py build`; evidence and command logs are written to
  `reports/latest/build.{json,md}` and `reports/latest/build.{stdout,stderr}.log`.
- CI installs ARM GNU Toolchain 14.2.Rel1, executes `doctor`, `check`, and `build`,
  then uploads the resulting reports and firmware artifacts from
  `.github/workflows/harness.yml`.
- Local verification on 2026-08-07: `doctor` and `check` exited 0. `build`
  correctly failed because the local environment does not yet provide the ARM GNU
  Toolchain; see `reports/latest/build.md` and `build.stderr.log`.

## Out of Scope

- FDCAN implementation
- FreeRTOS tasks
- Python Qt6 GUI
