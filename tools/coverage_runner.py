from __future__ import annotations

import shutil

from tools.common import LATEST_REPORT_DIR, REPO_ROOT, run_command
from tools.report_generator import write_reports
from tools.result import CheckResult, Status, print_results


TEST_PROJECT_DIR = REPO_ROOT / "firmware" / "tests"
LINE_COVERAGE_MINIMUM = 80
CRITICAL_LINE_COVERAGE_MINIMUM = 90
CRITICAL_SOURCE_ROOT = REPO_ROOT / "firmware" / "Services" / "can"


def run() -> int:
    """Run coverage-instrumented unit tests and enforce coverage thresholds."""
    results: list[CheckResult] = []
    ceedling = shutil.which("ceedling")
    gcovr = shutil.which("gcovr")
    project_file = TEST_PROJECT_DIR / "project.yml"

    if not ceedling or not gcovr:
        missing = ", ".join(name for name, tool in (("Ceedling", ceedling), ("gcovr", gcovr)) if not tool)
        results.append(CheckResult(
            name="coverage", status=Status.FAIL,
            message=f"Required coverage tools were not found in PATH: {missing}.",
        ))
    elif not project_file.is_file():
        results.append(CheckResult(
            name="coverage", status=Status.FAIL,
            message="Missing Ceedling project: firmware/tests/project.yml.",
            file="firmware/tests/project.yml",
        ))
    else:
        LATEST_REPORT_DIR.mkdir(parents=True, exist_ok=True)
        version = run_command([gcovr, "--version"], timeout_seconds=30)
        instrumented_tests = run_command(
            [ceedling, "gcov:all"], cwd=TEST_PROJECT_DIR, timeout_seconds=300,
        )
        coverage = run_command([
            gcovr,
            "--root", REPO_ROOT.as_posix(),
            "--filter", (REPO_ROOT / "firmware" / "App").as_posix(),
            "--filter", (REPO_ROOT / "firmware" / "Services").as_posix(),
            "--fail-under-line", str(LINE_COVERAGE_MINIMUM),
            "--xml-pretty",
            "--output", str(LATEST_REPORT_DIR / "coverage.xml"),
        ], cwd=TEST_PROJECT_DIR, timeout_seconds=120)
        critical_coverage = run_command([
            gcovr,
            "--root", REPO_ROOT.as_posix(),
            "--filter", CRITICAL_SOURCE_ROOT.as_posix(),
            "--fail-under-line", str(CRITICAL_LINE_COVERAGE_MINIMUM),
        ], cwd=TEST_PROJECT_DIR, timeout_seconds=120)
        (LATEST_REPORT_DIR / "coverage.stdout.log").write_text(
            instrumented_tests.stdout + coverage.stdout + critical_coverage.stdout,
            encoding="utf-8",
        )
        (LATEST_REPORT_DIR / "coverage.stderr.log").write_text(
            instrumented_tests.stderr + coverage.stderr + critical_coverage.stderr,
            encoding="utf-8",
        )

        if version.returncode != 0:
            results.append(CheckResult(
                name="coverage-version", status=Status.FAIL,
                message="gcovr --version could not be executed.",
            ))
        elif instrumented_tests.returncode != 0:
            results.append(CheckResult(
                name="coverage-test", status=Status.FAIL,
                message=f"Ceedling gcov:all failed with exit code {instrumented_tests.returncode}.",
                file="reports/latest/coverage.stderr.log",
            ))
        elif coverage.returncode != 0 or critical_coverage.returncode != 0:
            results.append(CheckResult(
                name="coverage", status=Status.FAIL,
                message=(f"gcovr did not meet the {LINE_COVERAGE_MINIMUM}% overall or "
                         f"{CRITICAL_LINE_COVERAGE_MINIMUM}% critical-source threshold."),
                file="reports/latest/coverage.xml",
            ))
        else:
            version_line = (version.stdout.strip() or version.stderr.strip()).splitlines()
            results.append(CheckResult(
                name="coverage", status=Status.PASS,
                message=(f"{version_line[0] if version_line else 'gcovr'} met the {LINE_COVERAGE_MINIMUM}% overall "
                         f"and {CRITICAL_LINE_COVERAGE_MINIMUM}% critical-source thresholds."),
                file="reports/latest/coverage.xml",
            ))

    exit_code = 0 if all(result.status == Status.PASS for result in results) else 1
    print_results(results)
    json_path, markdown_path = write_reports(
        report_name="coverage", command="python tools.py coverage",
        exit_code=exit_code, results=results,
    )
    print(f"[INFO] JSON report: {json_path}")
    print(f"[INFO] Markdown report: {markdown_path}")
    return exit_code
