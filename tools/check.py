from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path

from tools.architecture_check import collect_results as collect_architecture_results
from tools.common import REPO_ROOT, relative_to_repo, run_command
from tools.report_generator import write_reports
from tools.result import (
    CheckResult,
    Status,
    has_required_failure,
    print_results,
)


REQUIRED_PATHS = [
    Path("AGENTS.md"),
    Path("PROJECT.md"),
    Path("QUALITY_GATE.md"),
    Path("tools.py"),
    Path("docs/architectures"),
    Path("docs/requirements"),
    Path("docs/developments/CodingStyle.md"),
    Path("docs/exec-plans/active"),
    Path("docs/exec-plans/completed"),
    Path("firmware"),
    Path("pc_tool"),
    Path("tools"),
]

DOCUMENT_CONTRACTS: dict[Path, set[str]] = {
    Path("docs/README.md"): {"Documentation map"},
    Path("docs/requirements/REQ.md"): {"Functional requirements", "Quality attributes"},
    Path("docs/architectures/System.md"): {"Context", "Runtime flow"},
    Path("docs/architectures/Firmware.md"): {"Layers", "Build boundary"},
    Path("firmware/README.md"): {"Build", "Generated code"},
    Path("pc_tool/README.md"): {"Status", "Planned boundary"},
}

ACTIVE_PLAN_ROOT = REPO_ROOT / "docs/exec-plans/active"

ACTIVE_PLAN_REQUIRED_SECTIONS = [
    "Objective",
    "Scope",
    "Acceptance Criteria",
    "Verification Evidence",
    "Out of Scope",
]

AGENTS_FILE = REPO_ROOT / "AGENTS.md"

AGENT_COMMAND_PATTERN = re.compile(
    r"^\s*(?:python|python3|py)\s+tools\.py\s+([A-Za-z0-9_-]+)\s*$"
)
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)\s]+)(?:\s+[^)]*)?\)")
HARNESS_CONFIG = REPO_ROOT / "config" / "harness.toml"


def check_required_paths() -> list[CheckResult]:
    """
    檢查 Repository contract 所需路徑。
    """
    results: list[CheckResult] = []

    for relative_path in REQUIRED_PATHS:
        full_path = REPO_ROOT / relative_path

        if full_path.exists():
            results.append(
                CheckResult(
                    name="repository-path",
                    status=Status.PASS,
                    message="Required path exists.",
                    file=relative_path.as_posix(),
                )
            )
        else:
            results.append(
                CheckResult(
                    name="repository-path",
                    status=Status.FAIL,
                    message="Required path is missing.",
                    file=relative_path.as_posix(),
                )
            )

    return results


def check_document_contracts() -> list[CheckResult]:
    """Require core documents to contain their agreed minimum sections."""
    results: list[CheckResult] = []

    for relative_path, required_headings in DOCUMENT_CONTRACTS.items():
        full_path = REPO_ROOT / relative_path
        try:
            text = full_path.read_text(encoding="utf-8")
        except OSError as exc:
            results.append(CheckResult(
                name="document-read", status=Status.FAIL,
                message=f"Unable to read required document: {exc}",
                file=relative_path.as_posix(),
            ))
            continue

        headings = extract_markdown_headings(text)
        missing = sorted(
            heading for heading in required_headings
            if heading.casefold() not in headings
        )
        if missing:
            results.append(CheckResult(
                name="document-contract", status=Status.FAIL,
                message=f"Missing required sections: {', '.join(missing)}.",
                file=relative_path.as_posix(),
            ))
        else:
            results.append(CheckResult(
                name="document-contract", status=Status.PASS,
                message="Required document sections exist.",
                file=relative_path.as_posix(),
            ))

    return results


def check_document_links() -> list[CheckResult]:
    """Fail when a local Markdown link in a core document has no target."""
    results: list[CheckResult] = []
    documents = [REPO_ROOT / "README.md", AGENTS_FILE]
    documents.extend(REPO_ROOT / path for path in DOCUMENT_CONTRACTS)

    for document in documents:
        try:
            text = document.read_text(encoding="utf-8")
        except OSError as exc:
            results.append(CheckResult(
                name="document-link-read", status=Status.FAIL,
                message=f"Unable to read document links: {exc}",
                file=relative_to_repo(document),
            ))
            continue

        broken_links: list[str] = []
        for match in MARKDOWN_LINK_PATTERN.finditer(text):
            target = match.group(1)
            if target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            target_path = target.split("#", maxsplit=1)[0]
            if target_path and not (document.parent / target_path).exists():
                broken_links.append(target)

        if broken_links:
            results.append(CheckResult(
                name="document-links", status=Status.FAIL,
                message=f"Broken local links: {', '.join(broken_links)}.",
                file=relative_to_repo(document),
            ))
        else:
            results.append(CheckResult(
                name="document-links", status=Status.PASS,
                message="All local Markdown links resolve.",
                file=relative_to_repo(document),
            ))

    return results


def check_build_contract() -> list[CheckResult]:
    """Ensure the harness build configuration names a committed CMake preset."""
    try:
        with HARNESS_CONFIG.open("rb") as config_file:
            firmware = tomllib.load(config_file)["firmware"]
        project_dir = REPO_ROOT / str(firmware["project_dir"])
        configure_preset = str(firmware["configure_preset"])
        build_preset = str(firmware["build_preset"])
        artifact_path = Path(str(firmware["artifact"]))
        presets_path = project_dir / "CMakePresets.json"
        presets = json.loads(presets_path.read_text(encoding="utf-8"))
    except (KeyError, OSError, ValueError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        return [CheckResult(
            name="build-contract", status=Status.FAIL,
            message=f"Invalid build configuration: {exc}",
            file="config/harness.toml",
        )]

    configure_names = {
        preset.get("name") for preset in presets.get("configurePresets", [])
    }
    build_names = {
        preset.get("name") for preset in presets.get("buildPresets", [])
    }
    errors: list[str] = []
    if configure_preset not in configure_names:
        errors.append(f"unknown configure preset '{configure_preset}'")
    if build_preset not in build_names:
        errors.append(f"unknown build preset '{build_preset}'")
    if artifact_path.is_absolute():
        errors.append("artifact must be relative to the firmware project")

    if errors:
        return [CheckResult(
            name="build-contract", status=Status.FAIL,
            message="; ".join(errors) + ".", file="config/harness.toml",
        )]

    return [CheckResult(
        name="build-contract", status=Status.PASS,
        message="Harness build configuration matches committed CMake presets.",
        file="config/harness.toml",
    )]


def find_active_plans() -> list[Path]:
    """
    找出 active 目錄中的 Exec Plan。

    README.md 與隱藏檔不視為 Active Plan。
    """
    if not ACTIVE_PLAN_ROOT.exists():
        return []

    return sorted(
        path
        for path in ACTIVE_PLAN_ROOT.glob("*.md")
        if path.name.lower() != "readme.md"
        and not path.name.startswith(".")
    )


def check_active_plan_count() -> tuple[list[CheckResult], Path | None]:
    """
    Active Plan 必須剛好一份。
    """
    plans = find_active_plans()

    if len(plans) == 0:
        return (
            [
                CheckResult(
                    name="active-plan-count",
                    status=Status.FAIL,
                    message="No active execution plan was found.",
                    file=relative_to_repo(ACTIVE_PLAN_ROOT),
                )
            ],
            None,
        )

    if len(plans) > 1:
        plan_names = ", ".join(
            relative_to_repo(path)
            for path in plans
        )

        return (
            [
                CheckResult(
                    name="active-plan-count",
                    status=Status.FAIL,
                    message=(
                        "Exactly one active execution plan is required. "
                        f"Found {len(plans)}: {plan_names}"
                    ),
                    file=relative_to_repo(ACTIVE_PLAN_ROOT),
                )
            ],
            None,
        )

    return (
        [
            CheckResult(
                name="active-plan-count",
                status=Status.PASS,
                message="Exactly one active execution plan exists.",
                file=relative_to_repo(plans[0]),
            )
        ],
        plans[0],
    )


def extract_markdown_headings(text: str) -> set[str]:
    """
    取得 Markdown 標題文字，忽略大小寫。
    """
    headings: set[str] = set()

    for line in text.splitlines():
        match = re.match(r"^\s*#{1,6}\s+(.+?)\s*$", line)

        if match:
            headings.add(match.group(1).strip().casefold())

    return headings


def check_active_plan_sections(
    active_plan: Path | None,
) -> list[CheckResult]:
    """
    檢查 Active Plan 必要章節。
    """
    if active_plan is None:
        return []

    try:
        text = active_plan.read_text(
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        return [
            CheckResult(
                name="active-plan-read",
                status=Status.FAIL,
                message=f"Unable to read active plan: {exc}",
                file=relative_to_repo(active_plan),
            )
        ]

    headings = extract_markdown_headings(text)
    results: list[CheckResult] = []

    for section in ACTIVE_PLAN_REQUIRED_SECTIONS:
        if section.casefold() in headings:
            results.append(
                CheckResult(
                    name="active-plan-section",
                    status=Status.PASS,
                    message=f"Required section exists: {section}",
                    file=relative_to_repo(active_plan),
                )
            )
        else:
            results.append(
                CheckResult(
                    name="active-plan-section",
                    status=Status.FAIL,
                    message=f"Missing required section: {section}",
                    file=relative_to_repo(active_plan),
                )
            )

    return results


def read_agent_commands() -> tuple[list[str], list[CheckResult]]:
    """
    從 AGENTS.md 讀取 `python tools.py <command>`。
    """
    if not AGENTS_FILE.exists():
        return (
            [],
            [
                CheckResult(
                    name="agents-command-read",
                    status=Status.FAIL,
                    message="AGENTS.md does not exist.",
                    file="AGENTS.md",
                )
            ],
        )

    try:
        text = AGENTS_FILE.read_text(
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        return (
            [],
            [
                CheckResult(
                    name="agents-command-read",
                    status=Status.FAIL,
                    message=f"Unable to read AGENTS.md: {exc}",
                    file="AGENTS.md",
                )
            ],
        )

    commands: list[str] = []

    for line in text.splitlines():
        match = AGENT_COMMAND_PATTERN.match(line)

        if match:
            commands.append(match.group(1))

    if not commands:
        return (
            [],
            [
                CheckResult(
                    name="agents-command-read",
                    status=Status.FAIL,
                    message="No Harness command found in AGENTS.md.",
                    file="AGENTS.md",
                )
            ],
        )

    return (
        commands,
        [
            CheckResult(
                name="agents-command-read",
                status=Status.PASS,
                message=f"Found {len(commands)} Harness commands.",
                file="AGENTS.md",
            )
        ],
    )


def check_cli_commands(commands: list[str]) -> list[CheckResult]:
    """
    驗證 AGENTS.md 宣告的 CLI command 可以由 argparse 解析。

    使用 --help，避免真正執行 build、flash 或其他動作。
    """
    results: list[CheckResult] = []

    for command_name in commands:
        command = [
            sys.executable,
            "tools.py",
            command_name,
            "--help",
        ]

        process = run_command(
            command,
            cwd=REPO_ROOT,
            timeout_seconds=30,
        )

        display_command = (
            f"python tools.py {command_name} --help"
        )

        if process.returncode == 0:
            results.append(
                CheckResult(
                    name="agents-cli-command",
                    status=Status.PASS,
                    message=f"CLI command is valid: {display_command}",
                    file="AGENTS.md",
                )
            )
        else:
            error_message = (
                process.stderr.strip()
                or process.stdout.strip()
                or f"Exit code {process.returncode}"
            )

            results.append(
                CheckResult(
                    name="agents-cli-command",
                    status=Status.FAIL,
                    message=(
                        f"Invalid CLI command: {display_command}. "
                        f"{error_message}"
                    ),
                    file="AGENTS.md",
                )
            )

    return results


def collect_results() -> list[CheckResult]:
    """
    收集完整 Repository 與 Architecture 檢查結果。
    """
    results: list[CheckResult] = []

    results.extend(check_required_paths())
    results.extend(check_document_contracts())
    results.extend(check_document_links())
    results.extend(check_build_contract())

    plan_results, active_plan = check_active_plan_count()
    results.extend(plan_results)
    results.extend(check_active_plan_sections(active_plan))

    agent_commands, command_read_results = read_agent_commands()
    results.extend(command_read_results)
    results.extend(check_cli_commands(agent_commands))

    results.extend(collect_architecture_results())

    return results


def run() -> int:
    """
    執行 Repository Contract、Active Plan 與架構檢查。
    """
    results = collect_results()
    exit_code = 1 if has_required_failure(results) else 0

    print_results(results)

    json_path, markdown_path = write_reports(
        report_name="check",
        command="python tools.py check",
        exit_code=exit_code,
        results=results,
    )

    print(f"[INFO] JSON report: {json_path}")
    print(f"[INFO] Markdown report: {markdown_path}")

    return exit_code
