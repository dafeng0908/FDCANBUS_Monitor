# Protocol-Driven CAN Requirements

## REQ-PROTO-001 — single source of truth

The repository shall define CAN message encoding and UI presentation metadata in
`protocol/protocol.json`. Product-specific CAN bit mappings shall not be independently
maintained in firmware and PC source code.

**Verification:** `python tools.py protocol-check`.

## REQ-PROTO-002 — generate DBC

The protocol generator shall produce `generated/dbc/protocol.dbc` from the source protocol
document. The DBC shall contain message identifiers, DLC, signal bit locations, signedness,
factor, offset, range, and unit.

**Verification:** `python tools.py protocol-check`.

## REQ-PROTO-003 — generate UI page metadata

The protocol generator shall produce `generated/page/protocol.page.json`. Each UI item shall
refer to a protocol message and signal and define its page, group, widget type, order, display
precision, and unit.

**Verification:** `python tools.py protocol-check`.

## REQ-PROTO-004 — generate firmware C interface

The protocol generator shall produce C structures and encode/decode functions under
`generated/c/` using the same protocol definition used to generate the DBC.

**Verification:** `python tools.py protocol-check`; future firmware integration tests shall
verify generated encode/decode interoperability.

## REQ-PROTO-005 — reject stale generated artifacts

The quality gate shall fail when a generated DBC, page file, or C artifact does not exactly
match the current source protocol document.

**Verification:** `python tools.py quality`, which includes `protocol-check`.

## Protocol v1 limitations

Protocol v1 supports little-endian, byte-aligned 8/16/32-bit integer raw signals with linear
factor/offset conversion. Unsupported definitions are validation failures and shall not be
silently approximated.
