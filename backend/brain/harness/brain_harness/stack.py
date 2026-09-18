from __future__ import annotations

from typing import Literal, Optional

BrainStackRuntime = Literal["nextjs", "node", "go", "rust", "python"]

STACK_ALIASES: dict[str, BrainStackRuntime] = {
    "nextjs": "nextjs",
    "next.js": "nextjs",
    "next": "nextjs",
    "node": "node",
    "nodejs": "node",
    "js": "node",
    "go": "go",
    "golang": "go",
    "rust": "rust",
    "python": "python",
    "py": "python",
    "django": "python",
    "flask": "python",
}


def normalize_brain_stack(value: Optional[str]) -> Optional[BrainStackRuntime]:
    if not value:
        return None
    return STACK_ALIASES.get(str(value).strip().lower())


def stack_entry_files(stack: Optional[BrainStackRuntime]) -> list[str]:
    if stack == "nextjs":
        return ["app/page.tsx", "app/layout.tsx", "package.json"]
    if stack == "node":
        return ["src/index.ts", "index.js", "package.json"]
    if stack == "go":
        return ["go.mod", "main.go"]
    if stack == "rust":
        return ["Cargo.toml", "src/main.rs"]
    if stack == "python":
        return ["app.py", "requirements.txt", "pyproject.toml"]
    return ["README.md"]


def stack_default_entry_file(stack: Optional[BrainStackRuntime]) -> str:
    files = stack_entry_files(stack)
    return files[0] if files else "README.md"


STACK_GUIDANCE: dict[BrainStackRuntime, list[str]] = {
    "nextjs": [
        "This scaffold is a Next.js app. Put pages under app/. Do not invent a Vite config, React Router file, or a Express server.",
    ],
    "node": [
        "This scaffold is a plain Node.js app. Do not invent Next.js/React files or other frameworks unless the user asked for them.",
    ],
    "go": [
        "This scaffold is a Go project. Do not invent app/page.tsx or Express-style routes. Use main.go and the standard library.",
    ],
    "rust": [
        "This scaffold is a Rust project. Do not invent JavaScript/Python entrypoints. Use Cargo.toml and src/main.rs.",
    ],
    "python": [
        "This scaffold is a Python project. Do not invent app/page.tsx or Node/Go/React files. Use app.py and your requirements setup.",
    ],
}


def stack_guidance_lines(stack: Optional[BrainStackRuntime]) -> list[str]:
    if stack in STACK_GUIDANCE:
        return STACK_GUIDANCE[stack]
    return [
        "Match the existing scaffold. Do not invent files for a stack other than the one this repo is written in.",
    ]