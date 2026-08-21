from __future__ import annotations

import shutil

from tools.common import LATEST_REPORT_DIR, REPO_ROOT, run_command
from tools.report_generator import write_reports
from tools.result import CheckResult, Status, print_results


TEST_PROJECT_DIR = REPO_ROOT / "firmware" / "tests"


def run() -> int:
    """Run the repository's Ceedling unit-test suite."""
    results: list[CheckResult] = []
    ceedling = shutil.which("ceedling")
    project_file = TEST_PROJECT_DIR / "project.yml"

    if not ceedling:
        results.append(CheckResult(
            name="unit-test", status=Status.FAIL,
            message="Ceedling was not found in PATH.",
        ))
    elif not project_file.is_file():
        results.append(CheckResult(
            name="unit-test", status=Status.FAIL,
            message="Missing Ceedling project: firmware/tests/project.yml.",
            file="firmware/tests/project.yml",
        ))
    else:
        version = run_command([ceedling, "version"], timeout_seconds=30)
        process = run_command([ceedling, "test:all"], cwd=TEST_PROJECT_DIR, timeout_seconds=300)
        LATEST_REPORT_DIR.mkdir(parents=True, exist_ok=True)
        (LATEST_REPORT_DIR / "test.stdout.log").write_text(process.stdout, encoding="utf-8")
        (LATEST_REPORT_DIR / "test.stderr.log").write_text(process.stderr, encoding="utf-8")
        version_line = (version.stdout.strip() or version.stderr.strip()).splitlines()

        if version.returncode != 0:
            results.append(CheckResult(
                name="unit-test-version", status=Status.FAIL,
                message="ceedling version could not be executed.",
            ))
        elif process.returncode != 0:
            results.append(CheckResult(
                name="unit-test", status=Status.FAIL,
                message=f"Ceedling test:all failed with exit code {process.returncode}.",
                file="reports/latest/test.stderr.log",
            ))
        else:
            results.append(CheckResult(
                name="unit-test", status=Status.PASS,
                message=f"{version_line[0] if version_line else 'Ceedling'} test suite passed.",
                file="reports/latest/test.stdout.log",
            ))

    exit_code = 0 if all(result.status == Status.PASS for result in results) else 1
    print_results(results)
    json_path, markdown_path = write_reports(
        report_name="test", command="python tools.py test",
        exit_code=exit_code, results=results,
    )
    print(f"[INFO] JSON report: {json_path}")
    print(f"[INFO] Markdown report: {markdown_path}")
    return exit_code
