import subprocess
from typing import Tuple
from langchain_core.tools import tool

def _execute_command_raw(command: str) -> Tuple[str, bool]:
    """
    Internal helper to execute a shell command and capture its output.
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            shell=True,
            text=True,
            check=False,
            encoding='utf-8'
        )
        output = result.stdout + result.stderr
        success = result.returncode == 0
        return output.strip(), success
    except Exception as e:
        error_message = f"An internal error occurred: {e}"
        return error_message, False

DANGEROUS_KEYWORDS = ["rm -rf", "sudo", "apt remove", "yum remove", ":(){:|:&};:", "curl | sh"]

def _is_command_safe_blacklist(command: str) -> bool:
    """Checks if a command contains blacklisted keywords."""
    for keyword in DANGEROUS_KEYWORDS:
        if keyword in command.lower():
            return False
    return True

@tool
def shell_command_executor_raw(command: str) -> str:
    """
    Executes a shell command and returns its combined stdout and stderr.
    This tool should be used for simple, non-interactive commands.
    Security Warning: This command executes with shell=True and has a basic blacklist.
    Use with caution.
    """
    if not _is_command_safe_blacklist(command):
        return "Security Warning: This command contains blacklisted keywords and will not be executed."
    output_string, _ = _execute_command_raw(command)
    return output_string