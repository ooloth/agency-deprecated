from typing import TypedDict


class _ConfigRequired(TypedDict):
    max_iterations: int
    context: str


class Config(_ConfigRequired, total=False):
    # Prompt overrides — optional because commands fall back to their own defaults
    # when these keys are absent. Users can set them in .agent-loop.yml.
    analyze_prompt: str
    fix_prompt_template: str
    review_prompt: str


DEFAULT_CONFIG: Config = {
    "max_iterations": 5,
    "context": "",
}
