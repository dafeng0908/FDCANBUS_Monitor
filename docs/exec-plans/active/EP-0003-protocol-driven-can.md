# EP-0003 Protocol-Driven CAN Foundation

## Objective

Establish a document-driven CAN protocol workflow in which one version-controlled protocol
definition generates the DBC used for PC decoding, the page metadata used for Qt presentation,
and the C interface used by firmware.

## Requirements

- REQ-PROTO-001
- REQ-PROTO-002
- REQ-PROTO-003
- REQ-PROTO-004
- REQ-PROTO-005

## Scope

- Add `protocol/protocol.json` as the protocol single source of truth.
- Add deterministic protocol validation.
- Generate DBC, page JSON, and firmware C artifacts.
- Add `python tools.py protocol` and `python tools.py protocol-check`.
- Add `protocol-check` to `python tools.py quality`.
- Document the protocol-driven architecture and v1 limitations.

## Acceptance Criteria

- `python tools.py protocol` produces all expected generated artifacts.
- `python tools.py protocol-check` returns 0 when committed artifacts match the source.
- Changing the protocol document without regeneration causes `protocol-check` to fail.
- Invalid or unsupported signal definitions fail validation.
- `python tools.py quality` includes protocol consistency as part of completion.

## Current Step

Implementation is available on the protocol-driven feature branch and requires repository/CI
verification.

## Next Action

Run the full quality gate on the branch. After this plan is verified and completed, resume the
FDCAN RX vertical slice and make firmware/PC integration consume the generated protocol
artifacts.

## Last Verified Commit

Base commit before this change: `ffeb70542e6a44167138c480caadbc6d917400a6`.

## Verification Evidence

Pending execution of `python tools.py quality` on this change.

## Out of Scope

- Qt runtime implementation of the page factory.
- Runtime DBC decoding integration in the PC tool.
- Direct integration of generated C into the STM32 firmware target.
- Motorola/big-endian signals and non-byte-aligned signal packing.
