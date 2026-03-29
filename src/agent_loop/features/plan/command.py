import os
import subprocess

from agent_loop.domain.context import AppContext
from agent_loop.features.plan.prompts import PLAN_SYSTEM_PROMPT
from agent_loop.io.observability.logging import log

DEFAULT_PLAN_MODEL = "claude-opus-4-6"


def resolve_plan_model(config_model: str | None, cli_model: str | None) -> str:
    """Resolve the planning model: CLI flag > config > env var > hardcoded default."""
    if cli_model:
        return cli_model
    if config_model:
        return config_model
    return os.environ.get("ANTHROPIC_DEFAULT_OPUS_MODEL", DEFAULT_PLAN_MODEL)


def cmd_plan(ctx: AppContext, *, idea: str | None = None, model: str | None = None) -> None:
    """Launch an interactive planning session to produce a ralph-ready plan file."""
    plans_dir = ctx.project_dir / ".plans"
    plans_dir.mkdir(exist_ok=True)

    system_prompt = PLAN_SYSTEM_PROMPT
    if ctx.config.context:
        system_prompt = f"Project context:\n{ctx.config.context}\n\n{system_prompt}"

    resolved_model = resolve_plan_model(ctx.config.plan_model, model)

    log(
        f"📋 Planning session ({resolved_model}) — plans will be written to {plans_dir.relative_to(ctx.project_dir)}/"
    )

    cmd = ["claude", "--append-system-prompt", system_prompt, "--model", resolved_model]
    if idea:
        cmd.append(idea)

    subprocess.run(cmd, cwd=ctx.project_dir)
