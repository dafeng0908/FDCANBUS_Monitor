# EP-0001 Harness Bootstrap

## Objective

Establish the minimum executable development harness.

## Scope

- Normalize docs directory.
- Implement `tools.py` and its doctor, check, architecture, and build commands.
- Add project definition, quality gate, and initial CI workflow.
- Record machine-readable command evidence.

## Acceptance Criteria

- `python tools.py doctor` executes.
- `python tools.py check` executes.
- `python tools.py build` executes and verifies the ELF artifact.
- Missing external tools are reported without a false PASS.
- CI invokes the same local commands.

## Verification Evidence

- On 2026-08-12, Python 3.11.9 was installed and `python tools.py doctor` exited 0;
  evidence: `reports/latest/doctor.{json,md}`.
- On 2026-08-12, `python tools.py check` exited 0;
  evidence: `reports/latest/check.{json,md}`.
- On 2026-08-12, `python tools.py build` exited 0 and produced
  `firmware/FDCAN_TOOL_cmake/build/debug_GCC_NUCLEO-C542RC/FDCAN_TOOL.elf`;
  evidence: `reports/latest/build.{json,md}` and build logs.
- CI installs ARM GNU Toolchain 14.3.Rel1 and invokes doctor, check, and build through
  `.github/workflows/harness.yml`.

## Out of Scope

- FDCAN feature implementation.
- FreeRTOS tasks.
- Python Qt6 GUI.
