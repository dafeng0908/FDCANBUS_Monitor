# CANBUS Monitor Agent Guide

## Project Goal

Build an AI-assisted CAN FD development platform based on NUCLEO-C542RC.

## Active Plan

Read the active execution plan under:

docs/exec-plans/active/

## Architecture

docs/architectures/

## Requirements

docs/requirements/

## Protocol Contract

- `protocol/protocol.json` is the single source of truth for CAN message encoding and UI
  presentation metadata.
- Files under `generated/dbc/`, `generated/page/`, and `generated/c/` are generated artifacts.
- Never edit generated protocol artifacts manually.
- After changing the protocol document, run `python tools.py protocol` and then
  `python tools.py quality`.

## Mandatory Rules

- HAL APIs are allowed only in the BSP layer.
- Application and service modules must not include STM32 HAL headers.
- ISR code must not block, allocate memory, or call printf.
- Do not report PASS unless the command was actually executed.
- Every repository update must add a Markdown change record under `history/` named
  `YYYYMMDDHHMM_changelog.md`. The record must state its local date and time and list the
  updated items.

## Commands

python tools.py quality

## Definition of Done

- Relevant code and documents are updated.
- Generated protocol artifacts match `protocol/protocol.json`.
- `python tools.py quality` passes.
- Test and analysis results are linked from the generated quality report.
- The active execution plan is updated.
- A timestamped change record is added under `history/`.
