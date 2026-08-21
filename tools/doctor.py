from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

from tools.common import REPO_ROOT
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


def check_executable_version(
    executable: str,
    *,
    required: bool,
    display_name: str,
) -> CheckResult:
    """Run an executable's version command and return its reported version."""
    try:
        completed = subprocess.run(
            [executable, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return CheckResult(
            name=display_name,
            status=Status.FAIL if required else Status.WARN,
            message=f"Could not run {display_name} --version: {exc}",
            required=required,
        )

    output = completed.stdout.strip() or completed.stderr.strip()
    if completed.returncode != 0:
        return CheckResult(
            name=display_name,
            status=Status.FAIL if required else Status.WARN,
            message=(
                f"{display_name} --version exited {completed.returncode}: "
                f"{output or 'no output'}"
            ),
            required=required,
        )

    version_line = next(
        (line.strip() for line in output.splitlines() if line.strip()),
        "Version command succeeded.",
    )
    return CheckResult(
        name=display_name,
        status=Status.PASS,
        message=f"{executable} — {version_line}",
        required=required,
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
        return check_executable_version(
            tool_path,
            required=required,
            display_name=name,
        )

    return CheckResult(
        name=name,
        status=Status.FAIL if required else Status.WARN,
        message=f"{name} was not found in PATH.",
        required=required,
    )


def check_configured_arm_toolchain() -> CheckResult:
    """Check the configured compiler first, then the portable PATH lookup."""
    config_path = REPO_ROOT / "config" / "harness.toml"
    try:
        with config_path.open("rb") as config_file:
            tools = tomllib.load(config_file)["tools"]
        compiler_name = "arm-none-eabi-gcc.exe" if os.name == "nt" else "arm-none-eabi-gcc"
        compiler = Path(str(tools["arm_gnu_toolchain_bin"])) / compiler_name
    except (KeyError, OSError, tomllib.TOMLDecodeError) as exc:
        return CheckResult(
            name="ARM GNU Toolchain", status=Status.WARN,
            message=f"Configured toolchain could not be read: {exc}", required=False,
        )

    if compiler.is_file():
        return check_executable_version(
            str(compiler),
            required=False,
            display_name="ARM GNU Toolchain",
        )

    path_result = check_tool(
        "arm-none-eabi-gcc",
        required=False,
        display_name="ARM GNU Toolchain",
    )
    if not path_result.message.endswith("was not found in PATH."):
        return path_result

    return CheckResult(
        name="ARM GNU Toolchain", status=Status.WARN,
        message=f"Compiler not found at {compiler} or on PATH.", required=False,
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
        check_configured_arm_toolchain(),
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
