# Project_Name / Harness + ProjectFile migration

## Requested ownership model

```text
FDCANBUS_Monitor/
├── Harness/                 # AI-related development harness and management
└── ProjectFile/             # MCU source code, generated files, IDE, PC tool
```

GitHub requires `.github/workflows/` to remain in the repository root. Root `README.md`, `AGENTS.md`, `tools.py` (compatibility launcher), and `.gitignore` may also remain as thin entrypoints. These are exceptions, not additional project ownership domains.

## Verified current state

- MCU baseline: NUCLEO-C542RC / STM32CubeC5.
- Existing project: `firmware/FDCAN_TOOL_cmake/`, `firmware/FDCAN_TOOL.ioc2`.
- Host tools: `pc_tool/`.
- Current harness: `tools.py`, `tools/`, `config/`, `docs/`, `scripts/`, `prompts/`, `history/`, `reports/`.
- Root `.github/workflows/harness.yml` currently runs `python tools.py quality`.
- Existing checks have hard-coded paths to `firmware/`, `config/`, `docs/`, and `reports/`.

## Migration mapping

| Existing | Target | Responsibility |
|---|---|---|
| `firmware/` | `ProjectFile/firmware/` | MCU source, Cube/CMake/IDE files, embedded unit tests |
| `pc_tool/` | `ProjectFile/pc_tool/` | Host-side CAN monitor |
| `tools/` | `Harness/tools/` | Test/build/report CLI implementation |
| `config/` | `Harness/config/` | Harness settings |
| `docs/` | `Harness/docs/` | Requirements, architecture, plans, AI context |
| `scripts/` | `Harness/scripts/` | Automation scripts |
| `prompts/` | `Harness/prompts/` | Agent prompts |
| `history/` | `Harness/history/` | Required timestamped changelogs |
| `reports/` | `Harness/reports/` | Generated verification output |
| `tools.py` | root launcher → `Harness/tools.py` | Backward-compatible entrypoint |
| `AGENTS.md` | root policy → `Harness/agents/` | Root discoverability and detailed instructions |
| `.github/workflows/` | unchanged | GitHub Actions requires root discovery |

## Phase 1: safe scaffold (this PR)

- [x] Establish two ownership directories with explicit governance.
- [x] Record an exact path migration map.
- [x] Leave all working code and CI paths intact.
- [ ] CI validation after PR creation.
- [ ] Hardware validation is outside the scope of this PR.

## Phase 2: atomic migration (follow-up PR)

- [ ] Move folders with Git history-preserving operations where possible.
- [ ] Update CLI imports, `REPO_ROOT` semantics, and `config/harness.toml` paths.
- [ ] Update architecture/check/build/Cppcheck/Ceedling/gcovr path assumptions.
- [ ] Update CMake source/include paths and Ceedling `project.yml`.
- [ ] Update workflow artifact paths and .gitignore.
- [ ] Update Markdown relative links and quality-report links.
- [ ] Run `python tools.py doctor`, `check`, `build`, `cppcheck`, `test`, `coverage`, `quality`; record actual exit codes and evidence.
- [ ] Verify firmware CMake/CubeIDE configuration and CAN hardware behavior.
- [ ] Remove old paths only after checks succeed and target files are confirmed.

## Non-negotiable acceptance gate

Do not merge the phase-2 migration on the basis of layout alone. The quality gate must pass with actual evidence; if toolchains are missing, label verification incomplete. Do not silently treat a skipped build or test as PASS.
