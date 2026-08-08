from __future__ import annotations

import shutil
import sys

from tools.report_generator import write_reports
from tools.result import (
    CheckResult,
    Status,
    has_required_failure,
    print_results,
)


def check_python() -> CheckResult:
    """
    Python 3.11 以上視為通過。
    """
    minimum_version = (3, 11)
    current_version = sys.version_info[:2]

    if current_version >= minimum_version:
        return CheckResult(
            name="python",
            status=Status.PASS,
            message=f"Python {sys.version.split()[0]}",
        )

    return CheckResult(
        name="python",
        status=Status.FAIL,
        message=(
            f"Python {sys.version.split()[0]} detected; "
            "Python 3.11 or newer is required."
        ),
    )


def check_tool(
    command: str,
    *,
    required: bool,
    display_name: str | None = None,
) -> CheckResult:
    """
    檢查命令是否存在於 PATH。
    """
    name = display_name or command
    tool_path = shutil.which(command)

    if tool_path:
        return CheckResult(
            name=name,
            status=Status.PASS,
            message=tool_path,
            required=required,
        )

    return CheckResult(
        name=name,
        status=Status.FAIL if required else Status.WARN,
        message=f"{name} was not found in PATH.",
        required=required,
    )


def collect_results() -> list[CheckResult]:
    """
    收集開發環境檢查結果。
    """
    return [
        check_python(),
        check_tool(
            "git",
            required=True,
            display_name="Git",
        ),
        check_tool(
            "cppcheck",
            required=False,
            display_name="Cppcheck",
        ),
        check_tool(
            "ceedling",
            required=False,
            display_name="Ceedling",
        ),
        check_tool(
            "ruby",
            required=False,
            display_name="Ruby",
        ),
        check_tool(
            "gcovr",
            required=False,
            display_name="gcovr",
        ),
        check_tool(
            "cmake",
            required=False,
            display_name="CMake",
        ),
        check_tool(
            "ninja",
            required=False,
            display_name="Ninja",
        ),
        check_tool(
            "arm-none-eabi-gcc",
            required=False,
            display_name="ARM GNU Toolchain",
        ),
    ]


def run() -> int:
    """
    執行開發環境檢查並輸出報告。
    """
    results = collect_results()
    exit_code = 1 if has_required_failure(results) else 0

    print_results(results)

    json_path, markdown_path = write_reports(
        report_name="doctor",
        command="python tools.py doctor",
        exit_code=exit_code,
        results=results,
    )

    print(f"[INFO] JSON report: {json_path}")
    print(f"[INFO] Markdown report: {markdown_path}")

    return exit_code
