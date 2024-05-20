from os import environ
from subprocess import run as sp_run
from typing import Optional
import functools

PYTHON_CMD = environ.get("PYTHON_CMD", "python")  # python, python3, etc
ENV_SETUP_TOOL_DIR = "env_setup_tool.src"
ENV_SETUP_TOOL = "env_setup"
BASE_PYTHON_COMMAND = [PYTHON_CMD, "-m", f"{ENV_SETUP_TOOL_DIR}.{ENV_SETUP_TOOL}"]
BDD_CMD_LINE_OPTIONS = environ.get("BDD_CMD_LINE_OPTIONS", None)


@functools.cache
def run_env_setup_tool(
    feature: str,
    options: Optional[str] = BDD_CMD_LINE_OPTIONS,
    tool_cmd: str = "apply-configs",
):
    feature = feature.strip('"')
    cmd = BASE_PYTHON_COMMAND + [f"--feature={feature}"]

    if options is not None:
        option_list = options.split()
        for item in option_list:
            cmd.append(item)
    cmd.append(tool_cmd)

    print(f"Executing: {cmd}")

    completed_process = sp_run(cmd, capture_output=True, text=True)
    print(completed_process.stdout)

    if completed_process.returncode != 0:
        raise Exception(f"Error executing cmd_line_tool:\n{completed_process.stderr}")


def run(cmd: str) -> int:
    print(f"Executing: {cmd}")
    completed_process = sp_run(cmd, shell=True)
    print(f"Return Code: {completed_process.returncode}")
    return completed_process.returncode
