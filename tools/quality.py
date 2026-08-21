from __future__ import annotations

import sys
import tomllib

from tools.common import REPO_ROOT, run_command
from tools.report_generator import write_reports
from tools.result import CheckResult, Status, print_results


QUALITY_COMMANDS = ("doctor", "check", "build", "cppcheck", "test", "coverage")
DEFAULT_COMMAND_TIMEOUT_SECONDS = 60
BUILD_TIMEOUT_BUFFER_SECONDS = 60
DEFAULT_BUILD_PHASE_TIMEOUT_SECONDS = 600
COMMAND_TIMEOUTS = {
    "cppcheck": 180,
    "test": 360,
    "coverage": 600,
}


def command_timeout_seconds(command_name: str) -> int:
    """Return a timeout that accommodates each command's own execution contract."""
    if command_name != "build":
        return COMMAND_TIMEOUTS.get(command_name, DEFAULT_COMMAND_TIMEOUT_SECONDS)

    try:
        config_path = REPO_ROOT / "config" / "harness.toml"
        with config_path.open("rb") as config_file:
            phase_timeout = int(tomllib.load(config_file)["firmware"]["timeout_seconds"])
    except (KeyError, OSError, ValueError, tomllib.TOMLDecodeError):
        phase_timeout = DEFAULT_BUILD_PHASE_TIMEOUT_SECONDS

    return max(
        DEFAULT_COMMAND_TIMEOUT_SECONDS,
        (2 * phase_timeout) + BUILD_TIMEOUT_BUFFER_SECONDS,
    )


def run() -> int:
    """Run every completion check and publish the single quality decision."""
    results: list[CheckResult] = []

    for command_name in QUALITY_COMMANDS:
        timeout_seconds = command_timeout_seconds(command_name)
        process = run_command(
            [sys.executable, "tools.py", command_name],
            cwd=REPO_ROOT,
            timeout_seconds=timeout_seconds,
        )
        report_path = f"reports/latest/{command_name}.md"

        if process.returncode == 0:
            results.append(CheckResult(
                name=f"quality-{command_name}",
                status=Status.PASS,
                message=(
                    f"Executed python tools.py {command_name}; exited 0. "
                    f"Timeout: {timeout_seconds}s. Evidence: {report_path}."
                ),
                file=report_path,
            ))
        else:
            detail = process.stderr.strip() or process.stdout.strip()
            results.append(CheckResult(
                name=f"quality-{command_name}",
                status=Status.FAIL,
                message=(
                    f"Executed python tools.py {command_name}; exited "
                    f"{process.returncode} after a {timeout_seconds}s timeout. "
                    f"{detail[-500:]}"
                ),
                file=report_path,
            ))

    exit_code = 0 if all(result.status == Status.PASS for result in results) else 1
    print_results(results)
    json_path, markdown_path = write_reports(
        report_name="quality",
        command="python tools.py quality",
        exit_code=exit_code,
        results=results,
    )
    print(f"[INFO] JSON report: {json_path}")
    print(f"[INFO] Markdown report: {markdown_path}")
    return exit_code
