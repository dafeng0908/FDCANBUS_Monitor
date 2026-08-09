# Firmware

## Build

The firmware target is `FDCAN_TOOL` in `FDCAN_TOOL_cmake/`. `config/harness.toml` points to
the ARM GNU Toolchain bundled with STM32CubeIDE 2.2.0, so run `python tools.py build` from
the repository root without adding the compiler to the system PATH. The resulting ELF is
expected at `FDCAN_TOOL_cmake/build/debug_GCC_NUCLEO-C542RC/FDCAN_TOOL.elf`.

## Generated code

`FDCAN_TOOL.ioc2` and generated STM32 files are source inputs. Do not hand-edit generated
folders unless the generated-file workflow explicitly marks a file as user-modifiable.
Place product code behind the BSP, Services, and App boundaries documented in
[`docs/architectures/Firmware.md`](../docs/architectures/Firmware.md).
