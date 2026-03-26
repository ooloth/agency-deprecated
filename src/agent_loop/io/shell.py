import subprocess
import sys
from pathlib import Path

from agent_loop.domain.types import Label, LABEL_DESCRIPTIONS


def run(cmd: list[str], check: bool = True, capture: bool = True) -> str:
    """Run a command and return stdout."""
    result = subprocess.run(cmd, capture_output=capture, text=True)
    if check and result.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}", file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip() if capture else ""


def gh(*args: str) -> str:
    """Run a gh CLI command."""
    return run(["gh", *args])


def git(*args: str) -> str:
    """Run a git command."""
    return run(["git", *args])


# Read-only tools for analysis and review (no filesystem writes or shell execution)
_READ_ONLY_TOOLS = "Read,Glob,Grep"
# Tools needed to implement fixes (scoped to project dir via cwd)
_EDIT_TOOLS = "Read,Write,Edit,MultiEdit,Glob,Grep,Bash"


def claude(prompt: str, project_dir: Path, allowed_tools: str = _EDIT_TOOLS) -> str:
    """Run a prompt through the claude CLI with restricted tool access."""
    result = subprocess.run(
        ["claude", "-p", prompt, "--allowedTools", allowed_tools],
        capture_output=True,
        text=True,
        cwd=project_dir,
    )
    if result.returncode != 0:
        print(f"Claude failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def ensure_label(label: Label) -> None:
    """Ensure a label exists in the repo."""
    gh(
        "label",
        "create",
        label.value,
        "--force",
        "--description",
        LABEL_DESCRIPTIONS[label],
    )
