# Folder rules

Generated STM32 content remains under `firmware/FDCAN_TOOL_cmake/`. Hand-written firmware
uses `firmware/BSP/`, `firmware/Services/`, and `firmware/App/`; public headers belong in an
`include/` directory and implementation files in `src/`. Build outputs and harness reports
are generated artifacts and must not be committed.
