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
- `python tools.py check` reports no architecture violation.

## Verification Evidence

- On 2026-08-19, `python tools.py check` exited 0. It confirmed the App and Services layers
  have no forbidden HAL dependency and that the ISR rule has no violations; evidence:
  `reports/latest/check.{json,md}`.
- On 2026-08-19, `python tools.py build` exited 0 and produced
  `firmware/FDCAN_TOOL_cmake/build/debug_GCC_NUCLEO-C542RC/FDCAN_TOOL.elf`; evidence:
  `reports/latest/build.{json,md}` and build logs.

## Out of Scope

- FDCAN peripheral configuration, filter policy, and receive interrupt implementation.
- Receive queue implementation and unit tests.
- USB/UART forwarding, host protocol, and Qt GUI.
