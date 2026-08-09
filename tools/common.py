from __future__ import annotations

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Mapping, Sequence


# Repository 根目錄。
REPO_ROOT = Path(__file__).resolve().parents[1]

# 報告目錄。
REPORTS_ROOT = REPO_ROOT / "reports"
LATEST_REPORT_DIR = REPORTS_ROOT / "latest"
HISTORY_REPORT_DIR = REPORTS_ROOT / "history"


def ensure_report_directories() -> None:
    """
    建立 Harness 所需的報告目錄。
    """
    LATEST_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def current_timestamp() -> str:
    """
    取得含時區資訊的 ISO 8601 時間。
    """
    return datetime.now().astimezone().isoformat(timespec="seconds")


def get_git_commit() -> str:
    """
    取得目前 Repository 的 Git commit SHA。

    無法取得時回傳 UNKNOWN，不拋出例外。
    """
    result = run_command(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
    )

    if result.returncode != 0:
        return "UNKNOWN"

    commit = result.stdout.strip()
    return commit if commit else "UNKNOWN"


def run_command(
    command: Sequence[str],
    *,
    cwd: Path | None = None,
    timeout_seconds: int = 60,
    environment: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """
    執行外部命令。

    Args:
        command: 命令與參數。
        cwd: 工作目錄。
        timeout_seconds: timeout 秒數。

    Returns:
        subprocess.CompletedProcess。

    注意：
        這個函式不使用 check=True，呼叫者必須自行處理 exit code。
    """
    try:
        command_environment = os.environ.copy()
        if environment:
            command_environment.update(environment)

        return subprocess.run(
            list(command),
            cwd=cwd or REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            env=command_environment,
            check=False,
        )
    except FileNotFoundError as exc:
        return subprocess.CompletedProcess(
            args=list(command),
            returncode=127,
            stdout="",
            stderr=str(exc),
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""

        return subprocess.CompletedProcess(
            args=list(command),
            returncode=124,
            stdout=stdout,
            stderr=f"{stderr}\nCommand timeout after {timeout_seconds} seconds.",
        )


def relative_to_repo(path: Path) -> str:
    """
    將絕對路徑轉換成 Repository 相對路徑。
    """
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()
