# System architecture

## Context

CANBUS Monitor runs on a NUCLEO-C542RC target and is paired with a future Python Qt6 host
tool. The target owns CAN FD acquisition; the host tool owns operator interaction and
visualisation. The transport between them will be USB or UART.

## Runtime flow

1. Startup code initialises the MCU and board support package.
2. Firmware services receive CAN FD data and publish application-level events.
3. The host transport forwards selected events to the PC tool.
4. The PC tool displays monitoring state without directly controlling MCU HAL resources.

## Boundary rules

Only the BSP may include STM32 HAL headers or hold FDCAN handles. Application and service
layers must use interfaces owned by the BSP boundary. ISR handlers only signal or enqueue
work for later processing.
