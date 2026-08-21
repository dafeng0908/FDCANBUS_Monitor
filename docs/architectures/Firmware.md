# Firmware architecture

## Layers

- **BSP** owns STM32 HAL, peripherals, clocking, and interrupt glue.
- **Services** expose hardware-independent CAN FD and transport operations.
- **App** orchestrates product behaviour through service interfaces.

Hand-written firmware is rooted at `firmware/BSP/`, `firmware/Services/`, and
`firmware/App/`. The generated CMake entry point links all three roots. The architecture
checker requires each layer to contain source and rejects HAL dependencies in App and
Services.

## Build boundary

The committed build entry point is `firmware/FDCAN_TOOL_cmake/CMakePresets.json`. The
`debug_GCC_NUCLEO-C542RC` requires ARM GNU Toolchain. The build harness first checks the
optional CubeIDE path in `config/harness.toml`, then falls back to `arm-none-eabi-gcc` on
`PATH`; CI uses the latter. Both paths must report the pinned ARM GNU Toolchain 14.3.1
(GitHub release `14.3.Rel1`) before the build proceeds. Use `python tools.py quality` for
the completion decision rather than invoking an IDE-specific project path.
