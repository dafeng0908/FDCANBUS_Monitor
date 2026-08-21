from __future__ import annotations

import argparse
import sys
from collections.abc import Callable

from tools.architecture_check import run as run_architecture_check
from tools.build import run as run_build
from tools.check import run as run_check
from tools.doctor import run as run_doctor
from tools.quality import run as run_quality


Command = Callable[[], int]


def create_parser() -> argparse.ArgumentParser:
    """
    建立 CANBUS Monitor Harness 的命令列解析器。
    """
    parser = argparse.ArgumentParser(
        description="CANBUS Monitor development harness",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    subparsers.add_parser(
        "doctor",
        help="Check local development tools and environment",
    )

    subparsers.add_parser(
        "quality",
        help="Run the complete quality gate and publish the completion decision",
    )

    subparsers.add_parser(
        "check",
        help="Check repository contract, active plan and architecture rules",
    )

    subparsers.add_parser(
        "architectures",
        help="Run firmware architecture checks",
    )

    subparsers.add_parser(
        "build",
        help="Build firmware and PC tool",
    )

    return parser


def main() -> int:
    """
    Harness CLI 主入口。

    Returns:
        0：命令成功。
        非 0：命令失敗、環境缺失或功能尚未實作。
    """
    parser = create_parser()
    args = parser.parse_args()

    commands: dict[str, Command] = {
        "doctor": run_doctor,
        "quality": run_quality,
        "check": run_check,
        "architectures": run_architecture_check,
        "build": run_build,
    }

    command = commands.get(args.command)

    if command is None:
        parser.print_help()
        return 2

    try:
        return command()
    except KeyboardInterrupt:
        print("\n[FAIL] Command interrupted by user.")
        return 130
    except Exception as exc:
        print(f"[FAIL] Unexpected harness error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
