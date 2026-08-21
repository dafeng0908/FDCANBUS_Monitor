from __future__ import annotations

import shutil
from pathlib import Path

from tools.common import LATEST_REPORT_DIR, REPO_ROOT, run_command
from tools.report_generator import write_reports
from tools.result import CheckResult, Status, print_results


SOURCE_ROOTS = (
    REPO_ROOT / "firmware" / "App",
    REPO_ROOT / "firmware" / "Services",
    REPO_ROOT / "firmware" / "BSP",
)
INCLUDE_DIRS = (
    REPO_ROOT / "firmware" / "App" / "include",
    REPO_ROOT / "firmware" / "Services" / "can" / "include",
    REPO_ROOT / "firmware" / "BSP" / "include",
    REPO_ROOT / "firmware" / "FDCAN_TOOL_cmake",
)


def source_files() -> list[Path]:
    return sorted(
        file_path
        for root in SOURCE_ROOTS
        if root.is_dir()
        for file_path in root.rglob("*.c")
    )


def run() -> int:
    """Run Cppcheck against hand-written firmware sources."""
    results: list[CheckResult] = []
    cppcheck = shutil.which("cppcheck")
    files = source_files()

    if not cppcheck:
        results.append(CheckResult(
            name="cppcheck", status=Status.FAIL,
            message="Cppcheck was not found in PATH.",
        ))
    elif not files:
        results.append(CheckResult(
            name="cppcheck", status=Status.FAIL,
            message="No hand-written firmware C sources were found.",
        ))
    else:
        version = run_command([cppcheck, "--version"], timeout_seconds=30)
        version_line = (version.stdout.strip() or version.stderr.strip()).splitlines()
        command = [
            cppcheck,
            "--enable=warning,style,performance,portability",
            "--error-exitcode=1",
            "--inline-suppr",
            "--quiet",
            "--language=c",
            "--std=c11",
        ]
        command.extend(f"-I{include_dir}" for include_dir in INCLUDE_DIRS if include_dir.is_dir())
        command.extend(str(file_path) for file_path in files)
        process = run_command(command, timeout_seconds=120)
        LATEST_REPORT_DIR.mkdir(parents=True, exist_ok=True)
        (LATEST_REPORT_DIR / "cppcheck.stdout.log").write_text(process.stdout, encoding="utf-8")
        (LATEST_REPORT_DIR / "cppcheck.stderr.log").write_text(process.stderr, encoding="utf-8")

        if version.returncode != 0:
            results.append(CheckResult(
                name="cppcheck-version", status=Status.FAIL,
                message="cppcheck --version could not be executed.",
            ))
        elif process.returncode != 0:
            results.append(CheckResult(
                name="cppcheck", status=Status.FAIL,
                message=f"Cppcheck failed with exit code {process.returncode}.",
                file="reports/latest/cppcheck.stderr.log",
            ))
        else:
            results.append(CheckResult(
                name="cppcheck", status=Status.PASS,
                message=(
                    f"{version_line[0] if version_line else 'Cppcheck'} analyzed "
                    f"{len(files)} hand-written firmware source file(s)."
                ),
                file="reports/latest/cppcheck.stderr.log",
            ))

    exit_code = 0 if all(result.status == Status.PASS for result in results) else 1
    print_results(results)
    json_path, markdown_path = write_reports(
        report_name="cppcheck", command="python tools.py cppcheck",
        exit_code=exit_code, results=results,
    )
    print(f"[INFO] JSON report: {json_path}")
    print(f"[INFO] Markdown report: {markdown_path}")
    return exit_code
