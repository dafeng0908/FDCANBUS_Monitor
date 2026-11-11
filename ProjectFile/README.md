# ProjectFile — product files, firmware source, and IDE

This is the future canonical location for **MCU deliverables and project files**, kept separate from the AI/Harness tooling.

## Target layout (migration phase 2)

- `ProjectFile/firmware/BSP/`: STM32 HAL boundary and hardware adapters
- `ProjectFile/firmware/Services/`: hardware-independent CAN services
- `ProjectFile/firmware/App/`: application logic
- `ProjectFile/firmware/tests/`: Ceedling target-specific tests
- `ProjectFile/firmware/FDCAN_TOOL_cmake/`: Cube-generated/CMake MCU project
- `ProjectFile/firmware/FDCAN_TOOL.ioc2`: CubeMX/IDE project input
- `ProjectFile/pc_tool/`: Qt6 host monitor app

The existing target is **NUCLEO-C542RC (STM32C5)**, not STM32G4. Do not change MCU family, generated source, clocks, FDCAN timings, or IDE configuration during the directory-only migration.

## Phase 1 compatibility

Actual sources remain under `../firmware/` and `../pc_tool/` while the build/CI migration is prepared. This folder intentionally contains **no duplicate sources**. See `../MIGRATION_PLAN.md`.
