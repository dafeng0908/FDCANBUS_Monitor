# CANBUS Monitor requirements

## Functional requirements

- The firmware shall initialise the NUCLEO-C542RC platform before entering its main loop.
- The product shall provide a CAN FD monitoring workflow; protocol decoding and multi-device
  support are outside the MVP scope defined in [PROJECT.md](../../PROJECT.md).
- A future Qt6 host tool shall communicate with one attached target over USB or UART.

## Quality attributes

- Firmware application and service code shall not depend directly on STM32 HAL APIs.
- ISR code shall not block, allocate memory, or write to standard output.
- A firmware build, static analysis, unit tests, and coverage reports shall be reproducible
  through the local harness as the relevant capabilities are implemented.

## Traceability

Execution plans in `docs/exec-plans/` must reference affected requirements and record
verification evidence before being marked completed.
