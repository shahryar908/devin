from __future__ import annotations

OPENAI_TOOLS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "shell",
            "description": "Run a shell command inside the workspace (cwd is repo-relative). Keep commands short-lived.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The command to run."},
                    "cwd": {"type": "string", "description": "Repo-relative working directory (default: repo root)."},
                    "timeout": {"type": "integer", "description": "Timeout in seconds.", "minimum": 1},
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a UTF-8 text file, repo-relative path.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write a UTF-8 text file, repo-relative path. Creates parent directories.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List a directory, repo-relative path.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_commit",
            "description": "Create a commit with a Conventional Commits message. A bot trailer is added automatically.",
            "parameters": {
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_push",
            "description": "Push the current branch to origin.",
            "parameters": {
                "type": "object",
                "properties": {"branch": {"type": "string"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_open",
            "description": "Open a URL in the Devbox browser.",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "desktop_screenshot",
            "description": "Capture a desktop screenshot of the Devbox.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_memory",
            "description": "Persist short session facts to the control plane for later recall. Facts are filtered before saving.",
            "parameters": {
                "type": "object",
                "properties": {
                    "facts": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["facts"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "finish",
            "description": "Mark the task done and provide a final summary.",
            "parameters": {
                "type": "object",
                "properties": {"summary": {"type": "string"}},
            },
        },
    },
]


def tool_by_name(name: str) -> dict | None:
    for tool in OPENAI_TOOLS:
        if tool["function"]["name"] == name:
            return tool
    return None