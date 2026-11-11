# Harness — AI-assisted engineering workspace

This folder owns **AI instructions, development governance, build/test orchestration, traceability, and test evidence**. It must not become a second copy of MCU product sources.

## Target layout (migration phase 2)

- `Harness/agents/`: task-specific AI instructions and policies
- `Harness/config/`: test/build settings
- `Harness/docs/`: requirements, architecture, decisions, execution plans
- `Harness/scripts/`: CLI entrypoints and automation
- `Harness/tools/`: Python harness implementation
- `Harness/tests/`: host-side tests of harness behavior
- `Harness/reports/`: generated evidence (gitignored)
- `Harness/history/`: timestamped change records
- `Harness/prompts/`: reusable prompts

## Existing working paths (migration phase 1)

To avoid breaking the current quality gate, the existing `tools.py`, `tools/`, `config/`, `docs/`, `reports/`, `history/`, `prompts/`, `scripts/`, and `AGENTS.md` remain at their original paths **temporarily**. See `../MIGRATION_PLAN.md`.

## Mandatory rules

1. Read root `AGENTS.md` and the current active execution plan before making edits.
2. Keep STM32 HAL calls within BSP; ISR paths must be bounded and non-blocking.
3. Do not claim quality PASS unless the actual command ran and its exit code was 0.
4. Make source changes under `ProjectFile/` after path migration is verified.
5. Run `python tools.py quality` from repository root (until CLI migration is complete).
6. Record repository changes in the existing timestamped `history/` location until migrated.
