# Protocol-Driven CAN Architecture

## Principle

The CAN protocol document is the single source of truth. DBC, UI page metadata, and MCU
encode/decode code are generated artifacts and must not be maintained independently.

```text
protocol/protocol.json
        |
        +--> generated/dbc/protocol.dbc
        |        |
        |        +--> PC CAN decoder
        |
        +--> generated/page/protocol.page.json
        |        |
        |        +--> Qt page/group/widget factory
        |
        +--> generated/c/can_protocol_generated.[ch]
                 |
                 +--> Firmware protocol encode/decode
```

## Responsibilities

### Protocol document

Defines CAN message identifiers, DLC, signals, scaling, ranges, and UI presentation metadata.

### DBC

Defines how raw CAN payload bytes are decoded into physical signals. The PC application shall
not duplicate bit positions, scaling, or signedness in Python source code.

### Page document

Defines where decoded signals are presented. The PC application shall create pages and widgets
from this metadata rather than hard-code product-specific signal layouts.

### Generated C

Provides firmware-side message structures and encode/decode functions using the same signal
contract as the DBC.

## Harness contract

- `python tools.py protocol` validates the source document and regenerates all artifacts.
- `python tools.py protocol-check` validates the document and fails if any committed generated
  artifact is missing, stale, or manually modified.
- `python tools.py quality` includes `protocol-check`, so generated artifacts are part of the
  repository Definition of Done.
- Generated artifacts embed the SHA-256 of `protocol/protocol.json` for traceability.

## Evolution

Protocol v1 is intentionally narrow. New signal encodings or UI widget types must first extend
the protocol contract and validator, then add generator tests/evidence before use in a product
message.
