from __future__ import annotations

from brain_harness.stack import stack_default_entry_file
from brain_harness.tools.types import CommandRunner, ToolContext

MIN_PRODUCT_COMMITS = 3
MIN_ENTRY_BYTES = 250

SCAFFOLD_MARKER_GREP = (
    "grep -R -n -E 'TODO|FIXME' --include=*.py --include=*.ts --include=*.tsx "
    "--include=*.js --include=*.jsx --include=*.go --include=*.rs . 2>/dev/null | head -5"
)

PLACEHOLDER_README_MARKERS = (
    "hello from harness",
    "generated with the harness",
    "add your description here",
    "welcome to your next app",
)


async def check_product_finish_guards(ctx: ToolContext) -> tuple[bool, list[str]]:
    """Validate that a real product was built and committed.

    Approaches the devin product checks: enough focused commits, the scaffold
    entry file replaced by real code (non-trivial size), no leftover scaffold
    markers or placeholder README text, and — for Python — a clean compile.
    """
    problems: list[str] = []
    run: CommandRunner = ctx.run_command

    try:
        count = (await run("git rev-list --count HEAD 2>/dev/null || echo 0")).strip()
        commits = int(count or "0")
        if commits < MIN_PRODUCT_COMMITS:
            problems.append(
                f"only {commits} commit(s); product work needs at least {MIN_PRODUCT_COMMITS} focused commits"
            )
    except Exception as e:
        problems.append(f"could not read commit count: {e}")

    entry = stack_default_entry_file(ctx.stack_runtime)
    try:
        exists = (await run(f"test -f {entry} && echo yes || echo no")).strip()
        if exists != "yes":
            problems.append(f"expected entry file '{entry}' not found; scaffold was not replaced")
        else:
            try:
                size = int((await run(f"wc -c < {entry}")).strip() or "0")
                if size < MIN_ENTRY_BYTES:
                    problems.append(
                        f"entry file '{entry}' is only {size} bytes; likely an untouched scaffold"
                    )
            except Exception:
                pass
    except Exception as e:
        problems.append(f"could not verify entry file {entry}: {e}")

    try:
        leftovers = (await run(SCAFFOLD_MARKER_GREP)).strip()
        if leftovers:
            problems.append("scaffold markers (TODO/FIXME) are still present")
    except Exception:
        pass

    try:
        readme = (await run("head -c 600 README.md 2>/dev/null || true")).lower()
        if readme:
            for marker in PLACEHOLDER_README_MARKERS:
                if marker in readme:
                    problems.append(f"README still contains placeholder text '{marker}'")
                    break
    except Exception:
        pass

    if ctx.stack_runtime in ("python",):
        try:
            output = await run(
                f"python -m py_compile {entry} 2>&1 && echo PY_COMPILE_OK || echo PY_COMPILE_FAIL"
            )
            if "PY_COMPILE_OK" not in output:
                problems.append(f"entry file '{entry}' does not compile cleanly")
        except Exception:
            pass

    return (not problems, problems)