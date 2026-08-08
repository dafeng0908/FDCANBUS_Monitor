# CANBUS Monitor

An AI-assisted CAN FD development platform for the NUCLEO-C542RC.

## Quick start

1. Install Python 3.11+, Git, CMake, Ninja, and the `arm-none-eabi` GCC toolchain.
2. Run `python tools.py doctor` to verify the local environment.
3. Run `python tools.py check` to validate the repository contract and architecture rules.
4. Run `python tools.py build` to configure and build the committed CMake firmware preset.

Each command records JSON and Markdown evidence in `reports/latest/`. Build output is
also captured in `reports/latest/build.stdout.log` and `reports/latest/build.stderr.log`.

## Repository map

- `firmware/FDCAN_TOOL_cmake/` — STM32 firmware CMake project.
- `pc_tool/` — reserved home for the future Qt6 host application.
- `docs/` — requirements, architecture, development rules, and execution plans.
- `tools.py` and `tools/` — the local development harness.
- `config/harness.toml` — the single source of build configuration.

Read [AGENTS.md](AGENTS.md) before making changes. The release criteria are in
[QUALITY_GATE.md](QUALITY_GATE.md).
