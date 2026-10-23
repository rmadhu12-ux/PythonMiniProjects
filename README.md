# PythonMiniProjects

# MiniProject: API Todo Pipeline CLI

A small command-line tool that fetches a user's todos from a public REST API, validates every item with Pydantic, skips and logs bad items, and saves the clean data plus a summary as JSON. It retries only transient failures (timeouts, connection errors, HTTP 429 and 5xx) with exponential backoff.

## Features

- Fetches todos from [JSONPlaceholder](https://jsonplaceholder.typicode.com) using a reusable `httpx` client with a timeout
- Custom `@retry` decorator with exponential backoff that retries only transient errors (never 404 or 400)
- Pydantic validation of every item; invalid items are logged and skipped, not fatal
- Writes `todos_<user_id>.json` (valid todos) and `summary_<user_id>.json` (counts)
- `argparse` CLI with clean error messages and a non-zero exit code on failure
- Structured logging at INFO level, DEBUG with `--verbose`

## Setup

Requires Python 3.10 or newer.

```bash
# from the project root (the folder that contains MiniProject/)
python -m venv .venv

# Windows PowerShell
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

python -m pip install -r requirements.txt
```

## Usage

Run from the project root, not from inside `MiniProject/`:

```bash
python -m MiniProject.main --user-id 1
python -m MiniProject.main --user-id 1 --out-dir out
python -m MiniProject.main --user-id 1 --verbose
python -m MiniProject.main --help
```

| Option | Description | Default |
|---|---|---|
| `--user-id` | User whose todos to fetch (required, integer) | none |
| `--out-dir` | Folder for the output JSON files | `data` |
| `--verbose` | Show debug logging | off |

### Example run

```
$ python -m MiniProject.main --user-id 1
INFO:httpx:HTTP Request: GET https://jsonplaceholder.typicode.com/todos?userId=1 "HTTP/1.1 200 OK"
INFO:MiniProject.pipeline:fetched 20, valid 20, invalid 0, completed 11
{'userId': 1, 'fetched': 20, 'valid': 20, 'invalid': 0, 'completed': 11, 'pending': 9}
```

Output files:

```
data/
  todos_1.json      # the 20 validated todos
  summary_1.json    # counts of fetched, valid, invalid, completed, pending
```

## Project structure

```
wonders_rag/
  README.md
  requirements.txt
  .gitignore
  MiniProject/
    __init__.py
    client.py      # httpx client, is_transient, retry decorator, fetchTodos
    models.py      # Todo Pydantic model
    pipeline.py    # fetch, validate, summarize, write JSON
    main.py        # argparse entry point
  data/            # generated output (ignored by Git)
```

## How it handles failures

**Transient errors are retried.** Timeouts, connection errors, HTTP 429 and 5xx responses are retried up to 3 times, waiting 0.5s, then 1.0s between attempts. Non-transient errors such as 404 fail immediately, because the same request would fail again. `raise_for_status()` turns bad status codes into exceptions so the retry logic can see them.

**Bad data is skipped, not fatal.** Each item is validated with the `Todo` model. A failing item is logged as a warning and counted as invalid, and the remaining items are still processed.

**Failures exit cleanly.** If all retries fail, the CLI prints a short message and exits with code 1 instead of showing a traceback.

### Evidence

Validation: an item with missing fields (`{"id": 999}`) injected into the data:

```
WARNING:MiniProject.pipeline:skipping todo 999: 3 validation errors for Todo
userId
  Field required ...
```

The 20 real todos were still processed, and the summary showed `fetched 21, valid 20, invalid 1`.

Retry: client timeout forced to 0.001 seconds:

```
WARNING:MiniProject.client:attempt 1 failed: timed out, retrying in 0.5s
WARNING:MiniProject.client:attempt 2 failed: timed out, retrying in 1.0s
Request failed: timed out
```

The exit code was `1`. There is no third warning because the last attempt re-raises instead of sleeping.

Bad CLI input is handled by `argparse`:

```
$ python -m MiniProject.main
error: the following arguments are required: --user-id

$ python -m MiniProject.main --user-id abc
error: argument --user-id: invalid int value: 'abc'
```

## Limitations and next steps

- Only fetches todos from one public API; the endpoint and base URL are hard-coded.
- No automated tests yet. Next step: `pytest` tests for `is_transient`, `retry` (with a fake function that fails), and `run` (with a mocked client).
- Retries are sequential and have no jitter. Adding random jitter would help avoid synchronized retries.
- The retry decorator and validation pattern are reusable for calling an LLM API, which is the next project.

## Tech

Python, httpx, Pydantic v2, argparse, logging

## Testing

python -m pip install -r requirements-dev.txt
python -m pytest -v

Tests never call the real API. They use httpx.MockTransport for a fake server and patch time.sleep, so the whole suite runs in under a second.