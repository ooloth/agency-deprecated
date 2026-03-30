"""Watch command — poll for work in a continuous loop."""

import signal
import time

from agent_loop.domain.context import AppContext
from agent_loop.domain.errors import AgentLoopError
from agent_loop.domain.ports.agent_backend import AgentBackend
from agent_loop.features.analyze.command import cmd_analyze
from agent_loop.features.fix.command import cmd_fix
from agent_loop.io.observability.logging import log


def cmd_watch(
    ctx: AppContext,
    analysis_agent: AgentBackend,
    coding_agent: AgentBackend,
    review_agent: AgentBackend,
    interval: int,
    max_open_issues: int,
) -> None:
    """Poll for work: fix ready issues, analyze when queue is low.

    Catches AgentLoopError per iteration so a transient failure (bad network,
    flaky subprocess) doesn't kill the daemon. The error is logged and the
    loop continues on the next cycle.
    """
    stopping = False

    def handle_signal(_sig: int, _frame: object) -> None:
        nonlocal stopping
        stopping = True
        log.info("\n⏹️  Stopping after current step completes...")

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    log.info(
        "👀 Watching %s (interval=%ds, max_open=%d)",
        ctx.project_dir.name,
        interval,
        max_open_issues,
    )
    log.info("   Press Ctrl+C to stop gracefully.")
    log.info("")

    while not stopping:
        try:
            _poll_once(ctx, analysis_agent, coding_agent, review_agent, max_open_issues)
        except AgentLoopError as exc:
            log.info("❌ Error during poll: %s", exc)
            log.info("   Will retry next cycle.")

        if stopping:
            break

        # Sleep in small increments so Ctrl+C is responsive
        log.info("😴 Sleeping %ds...", interval)
        log.info("")
        for _ in range(interval):
            if stopping:
                break
            time.sleep(1)

    log.info("👋 Stopped.")


def _poll_once(
    ctx: AppContext,
    analysis_agent: AgentBackend,
    coding_agent: AgentBackend,
    review_agent: AgentBackend,
    max_open_issues: int,
) -> None:
    """Run one fix + analyze cycle. Exceptions propagate to the caller."""
    # Step 1: Fix any ready-to-fix issues
    cmd_fix(ctx, coding_agent, review_agent)

    # Step 2: Analyze if queue is below cap
    open_count = len(ctx.tracker.list_awaiting_review())

    if open_count >= max_open_issues:
        log.info(
            "⏸️  %d issue(s) awaiting review (cap: %d) — skipping analysis",
            open_count,
            max_open_issues,
        )
    else:
        log.info(
            "🔍 %d issue(s) awaiting review (cap: %d) — running analysis",
            open_count,
            max_open_issues,
        )
        cmd_analyze(ctx, analysis_agent)
