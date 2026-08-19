# Firmware

## Build

The firmware target is `FDCAN_TOOL` in `FDCAN_TOOL_cmake/`. `python tools.py build` first
uses the optional CubeIDE toolchain path in `config/harness.toml`; if it is unavailable, it
uses `arm-none-eabi-gcc` from `PATH`. This makes the same build command work locally and in
CI. The resulting ELF is expected at
`FDCAN_TOOL_cmake/build/debug_GCC_NUCLEO-C542RC/FDCAN_TOOL.elf`.

## Generated code

`FDCAN_TOOL.ioc2` and generated STM32 files are source inputs. Do not hand-edit generated
folders unless the generated-file workflow explicitly marks a file as user-modifiable.
Place product code behind the BSP, Services, and App boundaries documented in
[`docs/architectures/Firmware.md`](../docs/architectures/Firmware.md).
