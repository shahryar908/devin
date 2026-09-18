from __future__ import annotations

from brain_harness.stack import stack_default_entry_file
from brain_harness.tools.types import CommandRunner, ToolContext

MIN_PRODUCT_COMMITS = 3

SCAFFOLD_MARKER_GREP = (
    "grep -R -n -E 'TODO|FIXME' --include=*.py --include=*.ts --include=*.tsx "
    "--include=*.js --include=*.jsx --include=*.go --include=*.rs . 2>/dev/null | head -5"
)


async def check_product_finish_guards(ctx: ToolContext) -> tuple[bool, list[str]]:
    problems: list[str] = []

    try:
        count = (await ctx.run_command("git rev-list --count HEAD 2>/dev/null || echo 0")).strip()
        commits = int(count or "0")
        if commits < MIN_PRODUCT_COMMITS:
            problems.append(
                f"only {commits} commit(s); product work needs at least {MIN_PRODUCT_COMMITS} focused commits"
            )
    except Exception as e:
        problems.append(f"could not read commit count: {e}")

    entry = stack_default_entry_file(ctx.stack_runtime)
    try:
        exists = (await ctx.run_command(f"test -f {entry} && echo yes || echo no")).strip()
        if exists != "yes":
            problems.append(f"expected entry file '{entry}' not found; scaffold was not replaced")
    except Exception as e:
        problems.append(f"could not verify entry file {entry}: {e}")

    try:
        leftovers = (await ctx.run_command(SCAFFOLD_MARKER_GREP)).strip()
        if leftovers:
            problems.append("scaffold markers (TODO/FIXME) are still present")
    except Exception:
        pass

    return (not problems, problems)