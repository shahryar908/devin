from __future__ import annotations

import pytest

from brain_harness.tools.paths import (
    is_forbidden_path,
    resolve_repo_path,
    stack_check_path,
)


def test_resolve_repo_path_relative():
    assert resolve_repo_path("repo", "app/page.tsx") == "app/page.tsx"


def test_resolve_repo_path_absolute_is_relative_to_workspace():
    assert resolve_repo_path("/x/repo", "/etc/foo.txt") == "etc/foo.txt"


def test_resolve_repo_path_backslash_normalized():
    assert resolve_repo_path("repo", "app\\layout.tsx") == "app/layout.tsx"


def test_resolve_repo_path_dot_is_root():
    assert resolve_repo_path("repo", ".") == "."


def test_resolve_repo_path_rejects_traversal():
    with pytest.raises(ValueError):
        resolve_repo_path("repo", "../secret")


def test_resolve_repo_path_rejects_embedded_traversal():
    with pytest.raises(ValueError):
        resolve_repo_path("repo", "src/../../secret")


@pytest.mark.parametrize(
    "rel",
    [
        "node_modules/lodash/index.js",
        ".next/build/out.js",
        "src/__pycache__/x.py",
        ".venv/lib/python",
        "vendor/github.com/x/y",
    ],
)
def test_is_forbidden_path_blocks_deps_and_build_outputs(rel):
    assert is_forbidden_path(rel)


def test_is_forbidden_path_allows_source_files():
    assert not is_forbidden_path("src/App.tsx")
    assert not is_forbidden_path("app/layout.tsx")


def test_stack_check_path_allows_matching_stack():
    assert stack_check_path("app/page.tsx", "nextjs") is None


def test_stack_check_path_refuses_wrong_stack_file():
    text = stack_check_path("app/page.tsx", "go")
    assert text is not None and text.startswith("Refused:")
    assert "nextjs" in text


def test_stack_check_path_allows_unknown_path():
    assert stack_check_path("notes.md", "go") is None