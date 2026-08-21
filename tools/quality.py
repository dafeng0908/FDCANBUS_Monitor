from __future__ import annotations

import sys

from tools.common import REPO_ROOT, run_command
from tools.report_generator import write_reports
from tools.result import CheckResult, Status, print_results


QUALITY_COMMANDS = ("doctor", "check", "build")


def run() -> int:
    """Run every completion check and publish the single quality decision."""
    results: list[CheckResult] = []

    for command_name in QUALITY_COMMANDS:
        process = run_command(
            [sys.executable, "tools.py", command_name],
            cwd=REPO_ROOT,
            timeout_seconds=660,
        )
        report_path = f"reports/latest/{command_name}.md"

        if process.returncode == 0:
            results.append(CheckResult(
                name=f"quality-{command_name}",
                status=Status.PASS,
                message=(
                    f"Executed python tools.py {command_name}; exited 0. "
                    f"Evidence: {report_path}."
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
                    f"{process.returncode}. {detail[-500:]}"
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
