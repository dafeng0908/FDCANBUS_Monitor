# Quality Gate

## Stage 0

- [ ] `python tools.py quality` passes as the sole completion decision
- [ ] Required repository paths exist
- [ ] No command reports false PASS
- [ ] CI runs `python tools.py quality`

## Stage 1 Firmware

- [ ] Firmware build returns exit code 0
- [ ] Cppcheck unsuppressed errors = 0
- [ ] Ceedling tests pass
- [ ] Line coverage >= 80%
- [ ] Critical modules coverage >= 90%
- [ ] Architecture violations = 0

## Quality command graph

`python tools.py quality` executes `doctor`, `check`, `build`, `cppcheck`, `test`, and
`coverage` in order. All six commands must exit 0 before `quality.md` reports PASS.

## Evidence

Every PASS result must include:

- Command executed
- Timestamp
- Tool version
- Exit code
- Report path

The generated `reports/latest/quality.md` is the sole evidence entry point for completion. It
links the actual `doctor`, `check`, `build`, `cppcheck`, `test`, and `coverage` executions.
