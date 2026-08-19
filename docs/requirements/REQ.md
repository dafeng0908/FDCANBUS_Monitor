# CANBUS Monitor Requirements

## Scope and terminology

Stage 1 establishes a single-device CAN FD receive path on the NUCLEO-C542RC.
`Frame` means a CAN/CAN FD frame represented by identifier, identifier type, frame type,
payload length, payload bytes, and receive metadata. `BSP` means the only layer allowed to
use STM32 HAL types and APIs.

Unless a requirement says otherwise, its verification is performed by an automated test,
architecture check, or target-level test and the result is recorded under `reports/latest/`.

## Functional requirements

### REQ-FDCAN-001 — initialise the Stage 1 CAN FD path

The firmware shall initialise the NUCLEO-C542RC platform and FDCAN1 before the application
main loop begins. The BSP shall configure FDCAN1 for CAN FD with a nominal bit rate of
500 kbit/s and a data bit rate of 1 Mbit/s, then make receive processing available to the
Services layer.

**Acceptance criteria**

- On target boot, FDCAN1 starts without a HAL error and can receive an injected CAN FD frame.
- The generated configuration and the BSP configuration use the stated nominal and data rates.
- A startup failure is exposed through the service status; the application must not report the
  CAN receive path as ready.

**Verification:** target smoke test `T-FDCAN-001`; configuration review `T-FDCAN-002`.

### REQ-FDCAN-002 — preserve received CAN FD frames

The service shall accept standard (11-bit) and extended (29-bit) CAN FD data frames with a
payload length from 0 through 64 bytes. It shall preserve identifier type, identifier value,
payload length, and every payload byte while moving a frame from the BSP boundary into the
service receive queue.

**Acceptance criteria**

- Unit tests cover standard and extended identifiers and payload lengths 0, 8, and 64 bytes.
- For each accepted test frame, the dequeued frame exactly matches the injected frame fields.
- No product module outside `firmware/BSP/` exposes `FDCAN_HandleTypeDef` or a HAL header.

**Verification:** unit tests `T-FDCAN-010` through `T-FDCAN-014`; architecture check
`T-ARCH-001`.

### REQ-FDCAN-003 — apply an explicit receive-filter policy

The BSP shall configure receive filters from an explicit, version-controlled filter policy.
For Stage 1, the policy shall identify which standard and extended identifier ranges are
accepted and shall reject frames not matched by that policy. A policy change is a requirement
or configuration change and must update its verification test.

**Acceptance criteria**

- Target tests demonstrate that one identifier inside each configured accepted range is queued.
- Target tests demonstrate that an identifier outside every configured range is not queued.
- The test names the policy revision or configuration source it verifies.

**Verification:** target tests `T-FDCAN-020` and `T-FDCAN-021`.

### REQ-FDCAN-004 — keep interrupt work bounded

FDCAN interrupt handlers and HAL callbacks shall only acknowledge hardware events, copy
bounded frame data into the BSP-to-Service handoff, and update bounded counters or flags.
They shall not block, allocate or free memory, call `printf`/standard-output functions, or
invoke a delay API.

**Acceptance criteria**

- The architecture checker reports zero ISR-rule violations.
- Unit tests cover the handoff outcome for a received frame and a full queue.

**Verification:** architecture check `T-ARCH-002`; unit tests `T-FDCAN-030` and
`T-FDCAN-031`.

### REQ-FDCAN-005 — define loss behaviour under backpressure

The service shall use a bounded receive queue with a capacity of 32 frames. When the queue is
full, it shall drop the newly received frame, increment a monotonically increasing
`rx_dropped_frames` counter, and remain able to dequeue the 32 previously accepted frames.

**Acceptance criteria**

- A unit test fills the queue, submits one additional frame, and verifies that the counter
  increments once and that queue contents are unchanged.
- The counter is available through the service status interface without exposing HAL types.

**Verification:** unit test `T-FDCAN-040`.

### REQ-FDCAN-006 — expose CAN fault state

The BSP shall translate bus-off and controller communication-error events into a
hardware-independent service status containing: current state, last error category, and a
monotonically increasing error-event counter. Stage 1 shall not automatically recover from
bus-off.

**Acceptance criteria**

- A simulated or target-generated bus-off event changes the state to `BUS_OFF` and increments
  the error-event counter.
- An application-visible status read reports the state and last error category without a HAL
  dependency.

**Verification:** unit test `T-FDCAN-050`; target test `T-FDCAN-051` when hardware fault
injection is available.

## Quality attributes

### REQ-ARCH-001 — protect layer boundaries

Only `firmware/BSP/` may include STM32 HAL headers, call HAL APIs, or own FDCAN handles.
`firmware/Services/` shall expose hardware-independent frame, queue, and status interfaces;
`firmware/App/` shall depend only on those service interfaces.

**Verification:** `python tools.py check` reports zero architecture-boundary violations.

### REQ-QUAL-001 — produce reproducible evidence

The project shall provide repeatable local commands for environment diagnosis, repository and
architecture checking, firmware build, unit tests, static analysis, and coverage as the
capability is introduced. A successful result shall include the executed command, timestamp,
tool version, exit code, and report path.

**Verification:** `QUALITY_GATE.md` and the active execution plan record the commands and
their actual results; no command may report PASS without being executed.

## Stage 1 scope

- Add a BSP FDCAN1 adapter and its bounded receive handoff.
- Add a hardware-independent CAN service with a 32-frame receive queue and status interface.
- Add an application polling path that consumes service frames.
- Add the corresponding CMake targets, unit tests, static analysis, and coverage evidence.

## Out of scope for Stage 1

- Frame forwarding to USB or UART, and the Qt host GUI.
- FDCAN2, multi-device support, CANopen, J1939, and DBC decoding.
- Automatic bus-off recovery.

## Traceability

| Requirement | Planned verification | Evidence location |
| --- | --- | --- |
| REQ-FDCAN-001 | T-FDCAN-001, T-FDCAN-002 | `reports/latest/` |
| REQ-FDCAN-002 | T-FDCAN-010..014, T-ARCH-001 | `reports/latest/` |
| REQ-FDCAN-003 | T-FDCAN-020, T-FDCAN-021 | `reports/latest/` |
| REQ-FDCAN-004 | T-ARCH-002, T-FDCAN-030, T-FDCAN-031 | `reports/latest/` |
| REQ-FDCAN-005 | T-FDCAN-040 | `reports/latest/` |
| REQ-FDCAN-006 | T-FDCAN-050, T-FDCAN-051 | `reports/latest/` |
| REQ-ARCH-001 | `python tools.py check` | `reports/latest/check.{json,md}` |
| REQ-QUAL-001 | harness command reports | `reports/latest/` |

An execution plan that implements any requirement above must cite its requirement IDs and
record actual verification evidence before it is moved to `docs/exec-plans/completed/`.
