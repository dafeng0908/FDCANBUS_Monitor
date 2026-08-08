# Documentation map

This directory contains the maintained engineering knowledge for CANBUS Monitor.
Implementation decisions must be reflected here before a related execution plan is closed.

- `requirements/` defines externally observable behaviour and quality targets.
- `architectures/` defines system boundaries and allowed dependencies.
- `developments/` contains coding and repository rules.
- `exec-plans/` records active and completed implementation work.
- `tests/` defines the verification strategy.

The repository checks the minimum sections of the requirements, system, firmware, and
host-tool documents with `python tools.py check`.
