# Firmware architecture

## Layers

- **BSP** owns STM32 HAL, peripherals, clocking, and interrupt glue.
- **Services** expose hardware-independent CAN FD and transport operations.
- **App** orchestrates product behaviour through service interfaces.

The current generated CMake project provides startup and platform initialisation. App and
Services directories are introduced with their first production modules; their absence is
reported as a non-blocking bootstrap state by the architecture checker.

## Build boundary

The committed build entry point is `firmware/FDCAN_TOOL_cmake/CMakePresets.json`. The
`debug_GCC_NUCLEO-C542RC` preset requires ARM GNU Toolchain (`arm-none-eabi-gcc`) on PATH.
Use `python tools.py build` rather than invoking an IDE-specific project path.
