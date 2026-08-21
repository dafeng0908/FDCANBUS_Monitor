# EP-0002 Stage 1 Firmware Foundation

## Objective

Establish the BSP, Services, and App boundaries required to start the Stage 1 CAN FD receive
path without exposing STM32 HAL dependencies outside the BSP.

## Scope

- Add a BSP platform-initialisation adapter.
- Add hardware-independent CAN frame and service-status interfaces.
- Add an App runtime that initialises and polls Services only.
- Include all hand-written layers in the firmware CMake target.
- Require all three layers in the architecture checker.

## Acceptance Criteria

- `firmware/BSP/`, `firmware/Services/`, and `firmware/App/` each contain hand-written C
  source or header files.
- Only BSP includes generated STM32 platform headers.
- App includes Services interfaces and contains no HAL dependency.
- The CMake firmware target builds with the new source roots.
- `python tools.py quality` passes and reports no architecture violation.

## Current Step

Stage 1 firmware foundation is complete. The quality gate now runs environment, contract,
build, static-analysis, unit-test, and coverage checks as a single completion decision.

## Next Action

Implement the Stage 1 FDCAN1 BSP receive handoff and its hardware-independent Service queue.

## Last Verified Commit

`d4ed4178dc5f68a2f5adbd7c578aabf742ec1e95`

## Verification Evidence

- The completion decision is the automatically generated
  [`quality report`](../../../reports/latest/quality.md), which links the executed
  [`doctor`](../../../reports/latest/doctor.md), [`repository check`](../../../reports/latest/check.md),
  [`build`](../../../reports/latest/build.md), [`cppcheck`](../../../reports/latest/cppcheck.md),
  [`test`](../../../reports/latest/test.md), and [`coverage`](../../../reports/latest/coverage.md)
  reports.
- On 2026-08-21, `python tools.py quality` passed with a build timeout derived from both
  configured build phases plus a buffer; evidence: the generated
  [`quality report`](../../../reports/latest/quality.md).
- On 2026-08-21, the baseline Ceedling CAN Service suite passed and gcovr reported 100% line
  coverage for that service; evidence: the generated
  [`test report`](../../../reports/latest/test.md) and
  [`coverage report`](../../../reports/latest/coverage.md).

## Out of Scope

- FDCAN peripheral configuration, filter policy, and receive interrupt implementation.
- Receive queue implementation and unit tests.
- USB/UART forwarding, host protocol, and Qt GUI.
