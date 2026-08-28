# Quality Gate

## Stage 0

- [ ] `python tools.py quality` passes as the sole completion decision
- [ ] Required repository paths exist
- [ ] No command reports false PASS
- [ ] CI runs `python tools.py quality`

## Protocol Contract

- [ ] `protocol/protocol.json` validates
- [ ] Generated DBC matches the protocol document
- [ ] Generated UI page metadata matches the protocol document
- [ ] Generated C interface matches the protocol document
- [ ] Generated protocol artifacts are not stale or manually modified

## Stage 1 Firmware

- [ ] Firmware build returns exit code 0
- [ ] Cppcheck unsuppressed errors = 0
- [ ] Ceedling tests pass
- [ ] Line coverage >= 80%
- [ ] Critical modules coverage >= 90%
- [ ] Architecture violations = 0

## Quality command graph

`python tools.py quality` executes `doctor`, `check`, `protocol-check`, `build`, `cppcheck`,
`test`, and `coverage` in order. All seven commands must exit 0 before `quality.md` reports
PASS.

## Evidence

Every PASS result must include:

- Command executed
- Timestamp
- Tool version when applicable
- Exit code
- Report path

The generated `reports/latest/quality.md` is the sole evidence entry point for completion.
