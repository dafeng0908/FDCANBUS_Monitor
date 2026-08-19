from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from tools.common import REPO_ROOT, relative_to_repo
from tools.report_generator import write_reports
from tools.result import (
    CheckResult,
    Status,
    has_required_failure,
    print_results,
)


FIRMWARE_ROOT = REPO_ROOT / "firmware"

# App 與 Services 不允許直接使用 HAL。
LAYER_RULES: dict[str, list[tuple[str, re.Pattern[str]]]] = {
    "App": [
        (
            "HAL call outside BSP",
            re.compile(r"\bHAL_[A-Za-z0-9_]+\s*\("),
        ),
        (
            "STM32 HAL include outside BSP",
            re.compile(
                r'#\s*include\s*[<"][^">]*stm32c5xx_hal[^">]*[">]',
                re.IGNORECASE,
            ),
        ),
        (
            "FDCAN handle outside BSP",
            re.compile(r"\bFDCAN_HandleTypeDef\b"),
        ),
    ],
    "Services": [
        (
            "HAL call outside BSP",
            re.compile(r"\bHAL_[A-Za-z0-9_]+\s*\("),
        ),
        (
            "STM32 HAL include outside BSP",
            re.compile(
                r'#\s*include\s*[<"][^">]*stm32c5xx_hal[^">]*[">]',
                re.IGNORECASE,
            ),
        ),
        (
            "FDCAN handle outside BSP",
            re.compile(r"\bFDCAN_HandleTypeDef\b"),
        ),
    ],
}

PRODUCT_LAYER_NAMES = ("BSP", "Services", "App")

ISR_FUNCTION_PATTERN = re.compile(
    r"\b([A-Za-z_][A-Za-z0-9_]*(?:IRQHandler|Callback))\s*\([^;]*\)\s*\{"
)

ISR_FORBIDDEN_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "printf is forbidden inside ISR",
        re.compile(r"\bprintf\s*\("),
    ),
    (
        "malloc is forbidden inside ISR",
        re.compile(r"\bmalloc\s*\("),
    ),
    (
        "calloc is forbidden inside ISR",
        re.compile(r"\bcalloc\s*\("),
    ),
    (
        "realloc is forbidden inside ISR",
        re.compile(r"\brealloc\s*\("),
    ),
    (
        "free is forbidden inside ISR",
        re.compile(r"\bfree\s*\("),
    ),
    (
        "vTaskDelay is forbidden inside ISR",
        re.compile(r"\bvTaskDelay\s*\("),
    ),
    (
        "blocking delay is forbidden inside ISR",
        re.compile(r"\bHAL_Delay\s*\("),
    ),
]


@dataclass
class SanitizerState:
    in_block_comment: bool = False


def source_files(root: Path) -> list[Path]:
    """
    列出 C/C header 檔。
    """
    if not root.exists():
        return []

    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".c", ".h"}
    )


def sanitize_line(
    line: str,
    state: SanitizerState,
) -> str:
    """
    移除 C/C++ 註解與字串內容，以降低誤判。

    保留原始字元位置概念，但不做完整 C Parser。
    """
    output: list[str] = []
    index = 0

    while index < len(line):
        if state.in_block_comment:
            end_index = line.find("*/", index)

            if end_index == -1:
                return "".join(output)

            state.in_block_comment = False
            index = end_index + 2
            continue

        if line.startswith("/*", index):
            state.in_block_comment = True
            index += 2
            continue

        if line.startswith("//", index):
            break

        char = line[index]

        if char in {'"', "'"}:
            quote = char
            output.append(" ")
            index += 1

            while index < len(line):
                if line[index] == "\\":
                    index += 2
                    continue

                if line[index] == quote:
                    index += 1
                    break

                index += 1

            continue

        output.append(char)
        index += 1

    return "".join(output)


def sanitize_source(text: str) -> list[str]:
    """
    將來源檔轉換成移除註解與字串的行列表。
    """
    state = SanitizerState()

    return [
        sanitize_line(line, state)
        for line in text.splitlines()
    ]


def check_layer_rules() -> list[CheckResult]:
    """
    檢查 App 與 Services 是否違反 HAL 邊界。
    """
    results: list[CheckResult] = []

    if not FIRMWARE_ROOT.exists():
        return [
            CheckResult(
                name="firmware-root",
                status=Status.SKIP,
                message="Firmware directory does not exist yet.",
                required=False,
            )
        ]

    for layer_name in PRODUCT_LAYER_NAMES:
        layer_root = FIRMWARE_ROOT / layer_name
        layer_sources = source_files(layer_root)

        if not layer_root.exists() or not layer_sources:
            results.append(
                CheckResult(
                    name=f"architecture-layer-{layer_name.lower()}",
                    status=Status.FAIL,
                    message=f"{layer_name} layer must contain at least one C source or header file.",
                    file=relative_to_repo(layer_root),
                )
            )

    for layer_name, rules in LAYER_RULES.items():
        layer_root = FIRMWARE_ROOT / layer_name

        if not layer_root.exists():
            continue

        violations_before = len(
            [
                result
                for result in results
                if result.status == Status.FAIL
            ]
        )

        for file_path in source_files(layer_root):
            try:
                text = file_path.read_text(
                    encoding="utf-8",
                    errors="replace",
                )
            except OSError as exc:
                results.append(
                    CheckResult(
                        name="source-read",
                        status=Status.FAIL,
                        message=f"Unable to read source file: {exc}",
                        file=relative_to_repo(file_path),
                    )
                )
                continue

            sanitized_lines = sanitize_source(text)

            for line_number, line in enumerate(
                sanitized_lines,
                start=1,
            ):
                for rule_name, pattern in rules:
                    if pattern.search(line):
                        results.append(
                            CheckResult(
                                name="architecture-hal-boundary",
                                status=Status.FAIL,
                                message=rule_name,
                                file=relative_to_repo(file_path),
                                line=line_number,
                            )
                        )

        violations_after = len(
            [
                result
                for result in results
                if result.status == Status.FAIL
            ]
        )

        if violations_after == violations_before and source_files(layer_root):
            results.append(
                CheckResult(
                    name=f"architecture-layer-{layer_name.lower()}",
                    status=Status.PASS,
                    message=f"No forbidden HAL dependency found in {layer_name}.",
                )
            )

    return results


def check_isr_rules() -> list[CheckResult]:
    """
    檢查 IRQHandler 與 Callback 函式內禁止使用的 API。

    此處使用輕量級 brace-depth 分析，不取代正式 C parser。
    """
    results: list[CheckResult] = []

    if not FIRMWARE_ROOT.exists():
        return []

    violations = 0

    for file_path in source_files(FIRMWARE_ROOT):
        try:
            text = file_path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        except OSError as exc:
            results.append(
                CheckResult(
                    name="source-read",
                    status=Status.FAIL,
                    message=f"Unable to read source file: {exc}",
                    file=relative_to_repo(file_path),
                )
            )
            continue

        sanitized_lines = sanitize_source(text)

        in_isr = False
        brace_depth = 0
        isr_name = ""

        for line_number, line in enumerate(
            sanitized_lines,
            start=1,
        ):
            if not in_isr:
                match = ISR_FUNCTION_PATTERN.search(line)

                if match:
                    in_isr = True
                    isr_name = match.group(1)
                    brace_depth = (
                        line.count("{") - line.count("}")
                    )

                    for rule_name, pattern in ISR_FORBIDDEN_PATTERNS:
                        if pattern.search(line):
                            results.append(
                                CheckResult(
                                    name="architecture-isr-rule",
                                    status=Status.FAIL,
                                    message=f"{isr_name}: {rule_name}",
                                    file=relative_to_repo(file_path),
                                    line=line_number,
                                )
                            )
                            violations += 1

                    if brace_depth <= 0:
                        in_isr = False

                    continue

            else:
                for rule_name, pattern in ISR_FORBIDDEN_PATTERNS:
                    if pattern.search(line):
                        results.append(
                            CheckResult(
                                name="architecture-isr-rule",
                                status=Status.FAIL,
                                message=f"{isr_name}: {rule_name}",
                                file=relative_to_repo(file_path),
                                line=line_number,
                            )
                        )
                        violations += 1

                brace_depth += line.count("{")
                brace_depth -= line.count("}")

                if brace_depth <= 0:
                    in_isr = False
                    isr_name = ""
                    brace_depth = 0

    if violations == 0:
        results.append(
            CheckResult(
                name="architecture-isr-rule",
                status=Status.PASS,
                message="No forbidden blocking or allocation API found in ISR callbacks.",
            )
        )

    return results


def collect_results() -> list[CheckResult]:
    """
    收集所有架構檢查結果。
    """
    results: list[CheckResult] = []
    results.extend(check_layer_rules())
    results.extend(check_isr_rules())
    return results


def run() -> int:
    """
    執行架構檢查並輸出報告。
    """
    results = collect_results()
    exit_code = 1 if has_required_failure(results) else 0

    print_results(results)

    json_path, markdown_path = write_reports(
        report_name="architecture_check",
        command="python tools.py architecture",
        exit_code=exit_code,
        results=results,
    )

    print(f"[INFO] JSON report: {json_path}")
    print(f"[INFO] Markdown report: {markdown_path}")

    return exit_code
