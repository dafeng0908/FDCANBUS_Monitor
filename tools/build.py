from __future__ import annotations

import os
import shutil
import tomllib
from pathlib import Path

from tools.common import REPO_ROOT, run_command
from tools.report_generator import write_reports
from tools.result import CheckResult, Status, print_results


CONFIG_PATH = REPO_ROOT / "config" / "harness.toml"


def load_firmware_config() -> dict[str, object]:
    with CONFIG_PATH.open("rb") as config_file:
        config = tomllib.load(config_file)
    return config["firmware"]


def write_build_logs(stdout: str, stderr: str) -> None:
    reports = load_reports_config()
    for key, content in (("stdout_log", stdout), ("stderr_log", stderr)):
        path = REPO_ROOT / str(reports[key])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def load_reports_config() -> dict[str, object]:
    with CONFIG_PATH.open("rb") as config_file:
        config = tomllib.load(config_file)
    return config["reports"]


def configured_toolchain_bin() -> Path | None:
    """Return a configured toolchain directory when one is available."""
    try:
        with CONFIG_PATH.open("rb") as config_file:
            tools = tomllib.load(config_file)["tools"]
        return Path(str(tools["arm_gnu_toolchain_bin"]))
    except (KeyError, OSError, tomllib.TOMLDecodeError):
        return None


def find_arm_gnu_compiler() -> tuple[Path | None, Path | None]:
    """Find the compiler from the repository override or the current PATH.

    The optional repository setting supports a developer's CubeIDE installation.
    CI and other developer environments instead use the portable PATH lookup.
    """
    compiler_name = "arm-none-eabi-gcc.exe" if os.name == "nt" else "arm-none-eabi-gcc"
    configured_bin = configured_toolchain_bin()

    if configured_bin is not None and (configured_bin / compiler_name).is_file():
        return configured_bin / compiler_name, configured_bin

    path_compiler = shutil.which("arm-none-eabi-gcc")
    if path_compiler:
        compiler = Path(path_compiler)
        return compiler, compiler.parent

    return None, None


def run() -> int:
    """Configure and build the firmware using the committed CMake preset."""
    results: list[CheckResult] = []
    compiler, toolchain_bin = find_arm_gnu_compiler()

    if not CONFIG_PATH.exists():
        results.append(CheckResult(
            name="build-config", status=Status.FAIL,
            message="Missing config/harness.toml.", file="config/harness.toml",
        ))
    elif shutil.which("cmake") is None:
        results.append(CheckResult(
            name="cmake", status=Status.FAIL,
            message="CMake was not found in PATH.", file="config/harness.toml",
        ))
    elif compiler is None or toolchain_bin is None:
        message = (
            "ARM GNU Toolchain was not found in the configured "
            "arm_gnu_toolchain_bin path or on PATH."
        )
        results.append(CheckResult(
            name="arm-gnu-toolchain", status=Status.FAIL,
            message=message, file="config/harness.toml",
        ))
        write_build_logs("", message + "\n")
    else:
        try:
            config = load_firmware_config()
            project_dir = REPO_ROOT / str(config["project_dir"])
            configure_preset = str(config["configure_preset"])
            build_preset = str(config["build_preset"])
            timeout_seconds = int(config["timeout_seconds"])
        except (KeyError, OSError, tomllib.TOMLDecodeError, ValueError) as exc:
            results.append(CheckResult(
                name="build-config", status=Status.FAIL,
                message=f"Invalid firmware build configuration: {exc}",
                file="config/harness.toml",
            ))
        else:
            if not project_dir.is_dir():
                results.append(CheckResult(
                    name="firmware-project", status=Status.FAIL,
                    message="Configured firmware project directory is missing.",
                    file=str(config["project_dir"]),
                ))
            else:
                assert compiler is not None
                assert toolchain_bin is not None
                toolchain_environment = {
                    "PATH": (
                        str(toolchain_bin)
                        + os.pathsep
                        + os.environ.get("PATH", "")
                    ),
                }
                configure = run_command(
                    ["cmake", "--preset", configure_preset],
                    cwd=project_dir,
                    timeout_seconds=timeout_seconds,
                    environment=toolchain_environment,
                )
                stdout = configure.stdout
                stderr = configure.stderr
                if configure.returncode != 0:
                    results.append(CheckResult(
                        name="firmware-configure", status=Status.FAIL,
                        message=(f"cmake --preset {configure_preset} failed "
                                 f"with exit code {configure.returncode}."),
                        file=str(config["project_dir"]),
                    ))
                else:
                    build = run_command(
                        ["cmake", "--build", "--preset", build_preset],
                        cwd=project_dir,
                        timeout_seconds=timeout_seconds,
                        environment=toolchain_environment,
                    )
                    stdout += build.stdout
                    stderr += build.stderr
                    if build.returncode != 0:
                        results.append(CheckResult(
                            name="firmware-build", status=Status.FAIL,
                            message=(f"cmake --build --preset {build_preset} failed "
                                     f"with exit code {build.returncode}."),
                            file=str(config["project_dir"]),
                        ))
                    else:
                        artifact = project_dir / str(config["artifact"])
                        if artifact.is_file():
                            results.append(CheckResult(
                                name="firmware-build", status=Status.PASS,
                                message="Firmware built successfully; ELF artifact exists.",
                                file=str(config["artifact"]),
                            ))
                        else:
                            results.append(CheckResult(
                                name="firmware-artifact", status=Status.FAIL,
                                message="Build completed but the configured ELF artifact is missing.",
                                file=str(config["artifact"]),
                            ))
                write_build_logs(stdout, stderr)

    exit_code = 0 if all(result.status == Status.PASS for result in results) else 1
    print_results(results)
    json_path, markdown_path = write_reports(
        report_name="build", command="python tools.py build",
        exit_code=exit_code, results=results,
    )
    print(f"[INFO] JSON report: {json_path}")
    print(f"[INFO] Markdown report: {markdown_path}")
    return exit_code
