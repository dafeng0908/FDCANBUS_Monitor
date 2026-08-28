from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from tools.common import REPO_ROOT
from tools.report_generator import write_reports
from tools.result import CheckResult, Status, print_results


SPEC_PATH = REPO_ROOT / "protocol" / "protocol.json"
GENERATED_ROOT = REPO_ROOT / "generated"
OUTPUT_PATHS = {
    "dbc": GENERATED_ROOT / "dbc" / "protocol.dbc",
    "page": GENERATED_ROOT / "page" / "protocol.page.json",
    "c_header": GENERATED_ROOT / "c" / "can_protocol_generated.h",
    "c_source": GENERATED_ROOT / "c" / "can_protocol_generated.c",
}
SUPPORTED_SIGNAL_LENGTHS = {8, 16, 32}


def _load_spec() -> tuple[dict[str, Any], bytes]:
    raw = SPEC_PATH.read_bytes()
    return json.loads(raw.decode("utf-8")), raw


def _source_hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _parse_can_id(value: object) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value, 0)
    raise ValueError(f"CAN id must be int or string, got {type(value).__name__}.")


def _c_identifier(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", name).lower()


def _number(value: object) -> str:
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, int):
        return str(value)
    return f"{float(value):.12g}"


def _c_float(value: object) -> str:
    number = _number(value)
    if "." not in number and "e" not in number.lower():
        number += ".0"
    return f"{number}f"


def validate_spec(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    protocol = spec.get("protocol")
    messages = spec.get("messages")
    if not isinstance(protocol, dict):
        return ["Missing object: protocol."]
    if not isinstance(messages, list) or not messages:
        return ["messages must be a non-empty list."]

    for key in ("name", "version", "bus"):
        if not protocol.get(key):
            errors.append(f"protocol.{key} is required.")

    seen_message_names: set[str] = set()
    seen_message_ids: set[int] = set()

    for message_index, message in enumerate(messages):
        prefix = f"messages[{message_index}]"
        if not isinstance(message, dict):
            errors.append(f"{prefix} must be an object.")
            continue

        name = message.get("name")
        if not isinstance(name, str) or not name:
            errors.append(f"{prefix}.name is required.")
            continue
        if name in seen_message_names:
            errors.append(f"Duplicate message name: {name}.")
        seen_message_names.add(name)

        try:
            can_id = _parse_can_id(message.get("id"))
        except (TypeError, ValueError) as exc:
            errors.append(f"{prefix}.id is invalid: {exc}")
            continue

        if can_id < 0 or can_id > 0x1FFFFFFF:
            errors.append(f"{name}: CAN id must be between 0 and 0x1FFFFFFF.")
        if can_id in seen_message_ids:
            errors.append(f"Duplicate CAN id: 0x{can_id:X}.")
        seen_message_ids.add(can_id)

        dlc = message.get("dlc")
        if not isinstance(dlc, int) or dlc < 0 or dlc > 64:
            errors.append(f"{name}: dlc must be an integer from 0 to 64.")
            continue

        signals = message.get("signals")
        if not isinstance(signals, list) or not signals:
            errors.append(f"{name}: signals must be a non-empty list.")
            continue

        used_bits: set[int] = set()
        seen_signal_names: set[str] = set()

        for signal_index, signal in enumerate(signals):
            signal_prefix = f"{name}.signals[{signal_index}]"
            if not isinstance(signal, dict):
                errors.append(f"{signal_prefix} must be an object.")
                continue

            signal_name = signal.get("name")
            if not isinstance(signal_name, str) or not signal_name:
                errors.append(f"{signal_prefix}.name is required.")
                continue
            if signal_name in seen_signal_names:
                errors.append(f"{name}: duplicate signal name {signal_name}.")
            seen_signal_names.add(signal_name)

            start_bit = signal.get("start_bit")
            length = signal.get("length")
            if not isinstance(start_bit, int) or start_bit < 0:
                errors.append(f"{name}.{signal_name}: start_bit must be >= 0.")
                continue
            if length not in SUPPORTED_SIGNAL_LENGTHS:
                errors.append(
                    f"{name}.{signal_name}: protocol v1 supports lengths "
                    f"{sorted(SUPPORTED_SIGNAL_LENGTHS)} only."
                )
                continue
            if start_bit % 8 != 0:
                errors.append(
                    f"{name}.{signal_name}: protocol v1 requires byte-aligned start_bit."
                )
            if start_bit + length > dlc * 8:
                errors.append(f"{name}.{signal_name}: signal exceeds message DLC.")

            bits = set(range(start_bit, start_bit + length))
            if bits & used_bits:
                errors.append(f"{name}.{signal_name}: signal overlaps another signal.")
            used_bits |= bits

            if signal.get("endian") != "little":
                errors.append(f"{name}.{signal_name}: protocol v1 supports little endian only.")
            if not isinstance(signal.get("signed"), bool):
                errors.append(f"{name}.{signal_name}: signed must be true or false.")

            try:
                factor = float(signal.get("factor"))
                offset = float(signal.get("offset"))
                minimum = float(signal.get("min"))
                maximum = float(signal.get("max"))
            except (TypeError, ValueError):
                errors.append(
                    f"{name}.{signal_name}: factor, offset, min and max must be numeric."
                )
                continue

            if factor == 0.0:
                errors.append(f"{name}.{signal_name}: factor must not be zero.")
                continue
            if minimum > maximum:
                errors.append(f"{name}.{signal_name}: min must not exceed max.")

            signed = bool(signal.get("signed"))
            raw_low = (minimum - offset) / factor
            raw_high = (maximum - offset) / factor
            raw_min, raw_max = sorted((raw_low, raw_high))
            if signed:
                representable_min = -(1 << (length - 1))
                representable_max = (1 << (length - 1)) - 1
            else:
                representable_min = 0
                representable_max = (1 << length) - 1
            if raw_min < representable_min or raw_max > representable_max:
                errors.append(
                    f"{name}.{signal_name}: physical range does not fit {length}-bit "
                    f"{'signed' if signed else 'unsigned'} raw storage."
                )

            ui = signal.get("ui")
            if not isinstance(ui, dict):
                errors.append(f"{name}.{signal_name}: ui object is required.")
                continue
            for ui_key in ("page", "group", "widget", "order", "precision"):
                if ui_key not in ui:
                    errors.append(f"{name}.{signal_name}: ui.{ui_key} is required.")

    return errors


def _render_dbc(spec: dict[str, Any], source_hash: str) -> str:
    lines = [
        f'CM_ "AUTO GENERATED FROM protocol/protocol.json SHA256={source_hash}";',
        "",
    ]
    for message in spec["messages"]:
        can_id = _parse_can_id(message["id"])
        lines.append(
            f"BO_ {can_id} {message['name']}: {message['dlc']} Vector__XXX"
        )
        for signal in message["signals"]:
            sign = "-" if signal["signed"] else "+"
            lines.append(
                f" SG_ {signal['name']} : {signal['start_bit']}|{signal['length']}@1{sign} "
                f"({_number(signal['factor'])},{_number(signal['offset'])}) "
                f"[{_number(signal['min'])}|{_number(signal['max'])}] "
                f"\"{signal.get('unit', '')}\" Vector__XXX"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_page(spec: dict[str, Any], source_hash: str) -> str:
    pages: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for message in spec["messages"]:
        for signal in message["signals"]:
            ui = signal["ui"]
            groups = pages.setdefault(ui["page"], {})
            items = groups.setdefault(ui["group"], [])
            items.append(
                {
                    "signal": signal["name"],
                    "message": message["name"],
                    "widget": ui["widget"],
                    "order": ui["order"],
                    "precision": ui["precision"],
                    "unit": signal.get("unit", ""),
                }
            )

    page_document: dict[str, Any] = {
        "generated_from": "protocol/protocol.json",
        "source_hash": source_hash,
        "protocol_version": spec["protocol"]["version"],
        "pages": [],
    }
    for page_name in sorted(pages):
        groups_out: list[dict[str, Any]] = []
        for group_name in sorted(pages[page_name]):
            items = sorted(
                pages[page_name][group_name],
                key=lambda item: (item["order"], item["signal"]),
            )
            groups_out.append({"name": group_name, "items": items})
        page_document["pages"].append({"name": page_name, "groups": groups_out})

    return json.dumps(page_document, indent=2, ensure_ascii=False) + "\n"


def _render_c_header(spec: dict[str, Any], source_hash: str) -> str:
    lines = [
        "/* AUTO GENERATED FILE. DO NOT EDIT.",
        " * Source: protocol/protocol.json",
        f" * Source SHA256: {source_hash}",
        " */",
        "#ifndef CAN_PROTOCOL_GENERATED_H",
        "#define CAN_PROTOCOL_GENERATED_H",
        "",
        "#include <stdbool.h>",
        "#include <stdint.h>",
        "",
    ]
    for message in spec["messages"]:
        message_name = message["name"]
        message_ident = _c_identifier(message_name)
        can_id = _parse_can_id(message["id"])
        lines.extend(
            [
                f"#define CAN_{message_name}_ID (0x{can_id:X}u)",
                f"#define CAN_{message_name}_DLC ({message['dlc']}u)",
                "",
                "typedef struct",
                "{",
            ]
        )
        for signal in message["signals"]:
            lines.append(f"    float {_c_identifier(signal['name'])};")
        lines.extend(
            [
                f"}} can_{message_ident}_t;",
                "",
                (
                    f"bool can_{message_ident}_encode(const can_{message_ident}_t *message, "
                    f"uint8_t data[CAN_{message_name}_DLC]);"
                ),
                (
                    f"bool can_{message_ident}_decode("
                    f"const uint8_t data[CAN_{message_name}_DLC], "
                    f"can_{message_ident}_t *message);"
                ),
                "",
            ]
        )
    lines.extend(["#endif /* CAN_PROTOCOL_GENERATED_H */", ""])
    return "\n".join(lines)


def _render_c_source(spec: dict[str, Any], source_hash: str) -> str:
    lines = [
        "/* AUTO GENERATED FILE. DO NOT EDIT.",
        " * Source: protocol/protocol.json",
        f" * Source SHA256: {source_hash}",
        " */",
        '#include "can_protocol_generated.h"',
        "",
        "static uint32_t protocol_read_le(const uint8_t *data, uint8_t length)",
        "{",
        "    uint32_t value = 0u;",
        "    uint8_t index;",
        "    for (index = 0u; index < length; ++index)",
        "    {",
        "        value |= ((uint32_t)data[index]) << (8u * index);",
        "    }",
        "    return value;",
        "}",
        "",
        "static void protocol_write_le(uint8_t *data, uint8_t length, uint32_t value)",
        "{",
        "    uint8_t index;",
        "    for (index = 0u; index < length; ++index)",
        "    {",
        "        data[index] = (uint8_t)(value >> (8u * index));",
        "    }",
        "}",
        "",
        "static int32_t protocol_sign_extend(uint32_t value, uint8_t bits)",
        "{",
        "    if ((bits < 32u) && ((value & (1u << (bits - 1u))) != 0u))",
        "    {",
        "        value |= (~0u) << bits;",
        "    }",
        "    return (int32_t)value;",
        "}",
        "",
    ]

    for message in spec["messages"]:
        message_name = message["name"]
        message_ident = _c_identifier(message_name)
        lines.extend(
            [
                (
                    f"bool can_{message_ident}_encode(const can_{message_ident}_t *message, "
                    f"uint8_t data[CAN_{message_name}_DLC])"
                ),
                "{",
                "    uint8_t index;",
                "    if ((message == 0) || (data == 0))",
                "    {",
                "        return false;",
                "    }",
                f"    for (index = 0u; index < CAN_{message_name}_DLC; ++index)",
                "    {",
                "        data[index] = 0u;",
                "    }",
            ]
        )
        for signal in message["signals"]:
            byte_offset = signal["start_bit"] // 8
            byte_length = signal["length"] // 8
            signal_ident = _c_identifier(signal["name"])
            lines.extend(
                [
                    "    {",
                    f"        const float physical = message->{signal_ident};",
                    (
                        f"        if ((physical < {_c_float(signal['min'])}) || "
                        f"(physical > {_c_float(signal['max'])}))"
                    ),
                    "        {",
                    "            return false;",
                    "        }",
                    (
                        "        const int32_t raw_signed = "
                        f"(int32_t)((physical - {_c_float(signal['offset'])}) / "
                        f"{_c_float(signal['factor'])});"
                    ),
                    (
                        f"        protocol_write_le(&data[{byte_offset}], {byte_length}u, "
                        "(uint32_t)raw_signed);"
                    ),
                    "    }",
                ]
            )
        lines.extend(["    return true;", "}", ""])

        lines.extend(
            [
                (
                    f"bool can_{message_ident}_decode("
                    f"const uint8_t data[CAN_{message_name}_DLC], "
                    f"can_{message_ident}_t *message)"
                ),
                "{",
                "    if ((data == 0) || (message == 0))",
                "    {",
                "        return false;",
                "    }",
            ]
        )
        for signal in message["signals"]:
            byte_offset = signal["start_bit"] // 8
            byte_length = signal["length"] // 8
            signal_ident = _c_identifier(signal["name"])
            raw_expression = (
                f"protocol_read_le(&data[{byte_offset}], {byte_length}u)"
            )
            if signal["signed"]:
                raw_expression = (
                    f"protocol_sign_extend({raw_expression}, {signal['length']}u)"
                )
            lines.append(
                f"    message->{signal_ident} = ((float){raw_expression} * "
                f"{_c_float(signal['factor'])}) + {_c_float(signal['offset'])};"
            )
        lines.extend(["    return true;", "}", ""])

    return "\n".join(lines)


def render_outputs(spec: dict[str, Any], raw: bytes) -> dict[str, str]:
    source_hash = _source_hash(raw)
    return {
        "dbc": _render_dbc(spec, source_hash),
        "page": _render_page(spec, source_hash),
        "c_header": _render_c_header(spec, source_hash),
        "c_source": _render_c_source(spec, source_hash),
    }


def _validation_failure(command: str, report_name: str, errors: list[str]) -> int:
    results = [
        CheckResult(
            name="protocol-spec",
            status=Status.FAIL,
            message=error,
            file="protocol/protocol.json",
        )
        for error in errors
    ]
    print_results(results)
    write_reports(
        report_name=report_name,
        command=command,
        exit_code=1,
        results=results,
    )
    return 1


def run_generate() -> int:
    """Validate the source-of-truth protocol document and regenerate all artifacts."""
    command = "python tools.py protocol"
    try:
        spec, raw = _load_spec()
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return _validation_failure(command, "protocol", [f"Unable to load protocol spec: {exc}"])

    errors = validate_spec(spec)
    if errors:
        return _validation_failure(command, "protocol", errors)

    outputs = render_outputs(spec, raw)
    for key, output_path in OUTPUT_PATHS.items():
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(outputs[key], encoding="utf-8")

    result = CheckResult(
        name="protocol-generation",
        status=Status.PASS,
        message=(
            "Generated DBC, UI page metadata, and C encode/decode artifacts from "
            "protocol/protocol.json."
        ),
        file="protocol/protocol.json",
    )
    print_results([result])
    write_reports(
        report_name="protocol",
        command=command,
        exit_code=0,
        results=[result],
    )
    return 0


def run_check() -> int:
    """Verify the protocol document and confirm committed generated artifacts are current."""
    command = "python tools.py protocol-check"
    try:
        spec, raw = _load_spec()
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return _validation_failure(
            command, "protocol-check", [f"Unable to load protocol spec: {exc}"]
        )

    errors = validate_spec(spec)
    if errors:
        return _validation_failure(command, "protocol-check", errors)

    expected = render_outputs(spec, raw)
    results: list[CheckResult] = []
    for key, output_path in OUTPUT_PATHS.items():
        relative_path = output_path.relative_to(REPO_ROOT).as_posix()
        if not output_path.is_file():
            results.append(
                CheckResult(
                    name=f"protocol-generated-{key}",
                    status=Status.FAIL,
                    message=f"Generated artifact is missing: {relative_path}.",
                    file=relative_path,
                )
            )
            continue

        actual = output_path.read_text(encoding="utf-8")
        if actual != expected[key]:
            results.append(
                CheckResult(
                    name=f"protocol-generated-{key}",
                    status=Status.FAIL,
                    message=(
                        f"{relative_path} is stale or was edited manually. "
                        "Run python tools.py protocol."
                    ),
                    file=relative_path,
                )
            )
        else:
            results.append(
                CheckResult(
                    name=f"protocol-generated-{key}",
                    status=Status.PASS,
                    message=f"{relative_path} matches protocol/protocol.json.",
                    file=relative_path,
                )
            )

    exit_code = 0 if all(result.status == Status.PASS for result in results) else 1
    print_results(results)
    write_reports(
        report_name="protocol-check",
        command=command,
        exit_code=exit_code,
        results=results,
    )
    return exit_code
