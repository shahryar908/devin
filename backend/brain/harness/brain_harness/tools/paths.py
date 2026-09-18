from __future__ import annotations

from pathlib import PurePosixPath
from typing import Optional

FORBIDDEN_SEGMENTS = frozenset(
    {
        "node_modules",
        ".next",
        ".nuxt",
        "dist",
        "build",
        "out",
        "target",
        "vendor",
        "__pycache__",
        ".venv",
        "venv",
        ".dart_tool",
        ".cache",
        ".pytest_cache",
        "coverage",
        "deprecated-api",
        ".trunk",
    }
)

STACK_PATH_RULES: dict[str, str] = {
    "app/page.tsx": "nextjs",
    "app/layout.tsx": "nextjs",
    "pages/index.tsx": "nextjs",
    "vite.config.ts": "node",
    "vite.config.js": "node",
    "src/App.tsx": "node",
    "src/App.jsx": "node",
    "index.js": "node",
    "server.js": "node",
    "main.go": "go",
    "src/main.go": "go",
    "Cargo.toml": "rust",
    "src/main.rs": "rust",
    "app.py": "python",
    "manage.py": "python",
    "requirements.txt": "python",
    "setup.py": "python",
}


def _segments(rel: str) -> list[str]:
    path = PurePosixPath(rel)
    if path.is_absolute():
        path = path.relative_to(path.anchor)
    return list(path.parts)


def resolve_repo_path(work_dir: str, path: str) -> str:
    raw = str(path).replace("\\", "/")
    p = PurePosixPath(raw)
    if p.is_absolute():
        p = PurePosixPath(*p.parts[1:])
    parts = list(p.parts)
    if not parts or parts == [".", ""] or parts == ["."]:
        return "."
    if ".." in parts:
        raise ValueError("path escapes the workspace: .. traversal is not allowed")
    rel = p.as_posix()
    return rel


def is_forbidden_path(rel: str) -> bool:
    return any(part in FORBIDDEN_SEGMENTS for part in _segments(rel))


def stack_check_path(rel: str, stack: Optional[str]) -> Optional[str]:
    if not stack:
        return None
    rule_stack = STACK_PATH_RULES.get(rel)
    if rule_stack is None or rule_stack == stack:
        return None
    return (
        f"Refused: writing {rel} does not match this repo's stack ({stack}). "
        f"'{rel}' belongs to a '{rule_stack}' scaffold; keep work inside the active stack."
    )