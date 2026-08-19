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

## Mandatory Rules

- HAL APIs are allowed only in the BSP layer.
- Application and service modules must not include STM32 HAL headers.
- ISR code must not block, allocate memory, or call printf.
- Do not report PASS unless the command was actually executed.
- Every repository update must add a Markdown change record under `history/` named
  `YYYYMMDDHHMM_changelog.md`. The record must state its local date and time and list the
  updated items.

## Commands

python tools.py doctor
python tools.py check
python tools.py build

## Definition of Done

- Relevant code and documents are updated.
- Repository and architecture checks pass.
- Test and analysis results contain actual evidence.
- The active execution plan is updated.
- A timestamped change record is added under `history/`.
