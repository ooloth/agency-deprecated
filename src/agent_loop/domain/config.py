from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Settings loaded from .agent-loop.yml.

    All fields have defaults. Optional prompt overrides are None when absent —
    pipelines fall back to their own built-in defaults in that case.
    """

    max_iterations: int = 5
    context: str = ""

    # Prompt overrides — None means "use the built-in default".
    analyze_prompt: str | None = None
    fix_prompt_template: str | None = None
    review_prompt: str | None = None
