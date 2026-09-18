# brain-harness

Devin-style Brain agent harness: a full-fidelity Python port of the TS product
loop. A model is given a product request inside a sandboxed dev environment and
works through devbox tools until it finishes, with trust guards, conversation
compaction, commit hygiene, and product-implementation finish checks.

## Running

The harness needs a runtime. Pick one mode:

```sh
uv run --project . main.py "Implement a small REST API" \
  --stack python --requires-product --gateway-url http://localhost:8001
```

or via the installed console script:

```sh
brain-harness "Polish the landing page" --stack nextjs --worker-url http://localhost:9000
```

Modes:

- Gateway mode: `--gateway-url` (or `HARNESS_GATEWAY_URL`) points at a devbox
  tools gateway. `--runtime-url` / `HARNESS_RUNTIME_URL` is used as a fallback
  base when no gateway url is given.
- Worker mode: `--worker-url` (or `HARNESS_WORKER_URL`) routes every tool
  through an execution worker. When set, the gateway/runtime base is unused.

Other env vars: `HARNESS_MODEL` (default `gpt-4o`), `OPENAI_API_KEY`,
`HARNESS_WORKER_URL`, `HARNESS_GATEWAY_URL`, `HARNESS_RUNTIME_URL`.

## Runtime endpoint contract

The gateway exposes one HTTP endpoint per devbox tool, all JSON POST:

```
POST {base}/exec                 body {"command","cwd","timeout"}        -> {"output"}
POST {base}/read_file            body {"path"}                           -> {"content"}
POST {base}/write_file           body {"path","content"}                 -> {"content"}
POST {base}/list_dir             body {"path"}                           -> {"content"}
POST {base}/git_commit           body {"message"}                        -> {"output"}
POST {base}/git_push             body {"branch"}                         -> {"output"}
POST {base}/browser_open         body {"url"}                            -> {"output"}
POST {base}/desktop_screenshot   body {}                                 -> {"output"}
```

Errors come back as a non-2xx status or a JSON body carrying an `"error"` string.
The worker mirrors the same surface behind a task prefix:

```
POST {worker}/api/v1/tasks/{task_id}/exec     body {"command","cwd"}   -> {"output"}
POST {worker}/api/v1/tasks/{task_id}/tools    body {"name","args"}     -> {"content","done","summary"}
```

## Events

The harness emits `BrainHarnessEvent`s through `on_event`:
`agent.started`, `agent.log`, `agent.tool`, `agent.output`, `agent.completed`,
`agent.failed`.

## Tests

```sh
cd brain/harness && python -m pytest -q
```