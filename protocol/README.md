# Protocol-Driven CAN

`protocol/protocol.json` is the single source of truth for CAN protocol definitions.

Do not edit files under `generated/` manually. Regenerate them with:

```bash
python tools.py protocol
```

Verify that the specification is valid and every committed artifact is current with:

```bash
python tools.py protocol-check
```

The complete repository completion decision remains:

```bash
python tools.py quality
```

## Generated artifacts

- `generated/dbc/protocol.dbc` — signal encoding contract consumed by the PC decoder.
- `generated/page/protocol.page.json` — UI page/group/widget metadata.
- `generated/c/can_protocol_generated.h`
- `generated/c/can_protocol_generated.c`

## Protocol v1 constraints

The first generator version intentionally supports a narrow, deterministic subset:

- CAN/CAN FD message IDs up to 29 bits.
- DLC from 0 to 64 bytes.
- Little-endian signals only.
- Byte-aligned signals only.
- Signal lengths of 8, 16, or 32 bits.
- Signed or unsigned integer raw storage.
- Linear physical conversion using `physical = raw * factor + offset`.
- UI metadata containing page, group, widget, order, and precision.

Unsupported definitions fail validation instead of generating approximate output.
