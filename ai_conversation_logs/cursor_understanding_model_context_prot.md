# Understanding Model Context Protocol for server creation
_Exported on 9/24/2025 at 10:40:14 PDT from Cursor (1.6.45)_

---

**User**

I'm researching Model Context Protocol so that I can make my own MCP server. What can you tell me about MCP and how it works?

---

**Cursor**

### What MCP is (in a nutshell)
- **Model Context Protocol (MCP)** is an open, transport-agnostic protocol for connecting AI clients (e.g., IDEs, chat apps, agents) to external tools and data sources via standardized JSON-RPC methods.
- It cleanly separates roles:
  - **Client**: UI/agent that hosts the model and orchestrates calls.
  - **Server**: Exposes tools, data resources, and prompts the model can use.
- Built to be simple, secure-by-default, and composable across transports like stdio and WebSocket.

### Why MCP exists
- Avoids bespoke tool integrations per model/client.
- Standardizes capabilities (tools, file/data access, prompts, streaming, logging) so any MCP client can use any MCP server.

### Core concepts
- **Tools**: Parameterized actions callable by the model/user (e.g., “search issues”, “run query”). Each tool has a JSON Schema for inputs/outputs.
- **Resources**: Read-only or generated content that the model can fetch (e.g., files, HTTP content). Servers expose:
  - Concrete resources (URIs)
  - Optional resource templates (parameterized URIs with constraints)
- **Prompts**: Reusable prompt templates the client can request/fill.
- **Sampling**: A channel where the client can ask the server (if it has local model capabilities) to produce model text; optional.
- **Notifications**: Server → client log/status/progress updates; and subscriptions for resource change events.
- **Capabilities**: Declared at init so clients know which features the server supports.

### Transport and wire format
- **JSON-RPC 2.0** messages over:
  - **stdio** (common for local dev tools/CLIs)
  - **WebSocket** (common for services/remote)
- Request/response with ids; server may also send notifications (no id).

### Typical lifecycle
1. Client launches/connects to server.
2. `initialize`: Server declares name/version and capability flags.
3. Discovery:
   - `tools/list`, `resources/list`, `prompts/list`
   - Optional: `resources/templates` if supported
4. Usage:
   - `tools/call` to execute actions
   - `resources/read` for content
   - `prompts/get` for a filled prompt
   - `sampling/*` if server provides local model calls
5. Subscriptions (optional):
   - `resources/subscribe` → server sends update notifications
6. Teardown:
   - `shutdown` / connection close.

### Capability highlights
- Tools:
  - List tools with JSON Schemas.
  - Call tool with validated params; return structured result and optional text streams.
- Resources:
  - List/read resources by URI.
  - Declare safe roots and templates (e.g., file system whitelists).
  - Subscribe to change events.
- Prompts:
  - Enumerate prompt templates; get a concrete prompt with variables injected.
- Sampling (optional):
  - Expose local “model sampling” so the client can ask your server to generate text, often with tool-use integrated.
- Logging/Status:
  - Server can push log lines, status text, and progress.

### Security model (practical guidance)
- **Least privilege**: Only expose what’s needed. Prefer read-only resources unless your tool semantics require writes.
- **Explicit roots/templates**: For file access, lock to specific directories and vetted patterns.
- **Transport trust**: Authentication/authorization is out-of-scope for the spec—use transport-layer or process-level controls (e.g., OS perms, localhost only).
- **Schema validation**: Validate all tool params with JSON Schema; reject or sanitize unsafe inputs.
- **Rate/limits**: Implement basic timeouts and limits to avoid abuse.

### Building an MCP server (mental model)
- Pick a transport: stdio for local (simple), WebSocket for remote.
- Implement the initialization handshake and capability declaration.
- Implement the features you need:
  - Tools: define JSON Schemas, perform actions, return results.
  - Resources: expose URIs, read contents, optionally subscribe.
  - Prompts: return templates; fill with variables.
  - Sampling: optional, if you host/bridge a model.
- Add logging/status notifications for better UX.
- Write a small config/manifest so clients can auto-launch/connect.

### Minimal tool definition example
```json
{
  "name": "search_issues",
  "description": "Search project issues by query string",
  "input_schema": {
    "type": "object",
    "required": ["query"],
    "properties": {
      "query": { "type": "string", "minLength": 1 },
      "labels": { "type": "array", "items": { "type": "string" } },
      "limit": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 }
    },
    "additionalProperties": false
  }
}
```

### Example resource exposure
- Roots: `file://C:/Users/Administrator/Projects/MyRepo` (read-only)
- Resource: `file://…/README.md`
- Template: `file://…/{path}` with a constraint `path` matches `src/**.ts`

### Common server methods to implement
- `initialize`
- `tools/list`, `tools/call`
- `resources/list`, `resources/read`, `resources/subscribe` (optional)
- `prompts/list`, `prompts/get` (optional)
- `sampling/*` (optional)
- Notifications: `notifications/log`, `notifications/status`, `notifications/progress`

### Testing your server
- Run locally over stdio; connect with an MCP-compatible client.
- Verify:
  - Tool schemas validate/reject correctly
  - Resource reads stay within allowed roots
  - Subscriptions deliver updates
  - Logs/status appear in the client
- Add structured error responses with meaningful codes/messages.

### When to use MCP
- You want one integration that works with multiple AI clients.
- You have tools/data to expose behind a stable, model-agnostic interface.
- You need fine-grained control over what a model can access and how.

If you want, I can scaffold a minimal MCP server (Node or Python), wired for stdio, with one tool and a safe file resource root—just tell me your preferred language and use case.

```json
{
  "name": "search_issues",
  "description": "Search project issues by query string",
  "input_schema": {
    "type": "object",
    "required": ["query"],
    "properties": {
      "query": { "type": "string", "minLength": 1 },
      "labels": { "type": "array", "items": { "type": "string" } },
      "limit": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 }
    },
    "additionalProperties": false
  }
}
```

---

**User**

I'm going to build a MCP server that will interact with this IDE 'Cursor'.  What are some ways I could implement this? 

---

**Cursor**

### High-level options to integrate an MCP server with Cursor
- **Local stdio server (recommended for dev tools)**
  - Cursor launches your server as a child process and communicates over stdio.
  - Best for file-system tools, build/test runners, linters, git, and other local actions.
  - Simple to distribute (just a CLI). Good security by OS permissions and explicit allow-listing.

- **Local/remote WebSocket server**
  - Cursor connects to `ws://` or `wss://` URL.
  - Good when tools live in a service (CI, issues, docs, internal APIs).
  - Add auth (token/mTLS) at the transport layer.

- **Hybrid (stdio + remote)**
  - A local stdio server exposes local tools and also proxies selected remote APIs.
  - Keeps secrets in one place; centralizes rate-limiting and caching.

- **Sidecar daemon + stdio shim**
  - Long-lived daemon maintains watchers, caches, sessions.
  - A thin stdio process is launched by Cursor and relays to the daemon.
  - Useful for fast file-change subscriptions and persistent auth flows.

### What to expose to Cursor via MCP
- **Tools (actions)**
  - Files: read/write, create/delete, search/grep, refactors, format/lint, codegen.
  - Dev workflow: run tests, coverage, build, package scripts, docker, task runners.
  - Git: status/diff, commit, branch, stash, cherry-pick, PR creation.
  - Project intel: dependency graph, symbol index, dead code finder.
  - External: issue tracker, CI status, artifact fetch, docs search.
- **Resources (read-only URIs)**
  - Safe roots: workspace directory; selected caches/logs; build outputs.
  - Virtual resources: aggregated reports (test summaries, dependency trees).
  - Templates: `file://{path}` with constraints; `issue://{id}` etc.
- **Prompts**
  - Reusable templates for things like “create test”, “write commit message”, “triage failure”.
- **Subscriptions**
  - File changes, git HEAD changes, CI status updates. Push notifications improve UX.
- **Sampling (optional)**
  - Only if your server also hosts a model; otherwise skip.

### Choosing transport and packaging
- **Windows-first local tooling**: stdio CLI is easiest. Package with Node (TypeScript SDK) or Python.
- **Org-wide/internal tools**: WebSocket with token auth and per-project config.
- **Performance-sensitive**: sidecar daemon with watchers; stdio shim for Cursor.

### Practical implementation stacks
- **Node/TypeScript**
  - Use `@modelcontextprotocol/sdk` for quick scaffolding, JSON Schema validation, and transport helpers.
  - Pros: rich ecosystem for dev tooling (eslint, prettier, ts-morph), good Windows support.
- **Python**
  - Use the official `mcp` Python package.
  - Pros: scripting, data tooling, test frameworks, simple subprocess orchestration.

### Minimal capability set that works well in Cursor
- Tools:
  - `search_in_workspace({ query, glob, limit })`
  - `read_file({ path, encoding })`, `write_file({ path, content, create })`
  - `run_command({ cmd, args, cwd, timeout })` with allow-list
  - `git_diff({ pathspec, staged })`, `git_commit({ message, addAll })`
- Resources:
  - `file://…` under an explicit safe root (the workspace)
  - `virtual://test-summary` and `virtual://lint-report`
- Subscriptions:
  - `resources/subscribe` to `file://**/*` within the root, debounced

### How Cursor typically connects
- Add an MCP server entry in Cursor’s settings to either:
  - Launch a local command (stdio): command + args + env.
  - Connect to a WebSocket URL: `ws://localhost:PORT` (optionally with headers).
- Provide a short README with the exact settings snippet and prerequisites (Node/Python path).

### Security and safety defaults
- Explicit safe roots for any file access; reject paths outside roots.
- JSON Schema validation for every tool input; `additionalProperties: false`.
- Command execution: allow-list commands; timeouts; max output size.
- Redact secrets in logs; never echo env vars by default.

### Testing in Cursor
- Verify `initialize` advertises the right capabilities.
- `tools/list` shows your tools with clear descriptions.
- Run quick flows: search → open → edit → format → test → commit.
- Try malformed inputs and confirm structured errors.
- Check subscriptions trigger on file changes.

### Deployment patterns with examples
- Local stdio CLI:
  - Package a single `mcp-dev-tools` binary (Node or Python).
  - Cursor config points to it; no network required.
- Remote WebSocket service:
  - `wss://mcp.company.com` exposes org APIs (issues, CI).
  - Local stdio server focuses on workspace/file ops; both can be added to Cursor.

### Next step offers
- I can scaffold a minimal server (Node or Python) with:
  - stdio transport
  - safe workspace root
  - `search_in_workspace`, `read_file`, `write_file`, `run_command` (allow-list), `git_diff`
  - resource template for `file://{path}`
  - subscription to file changes
- Tell me your preferred language and initial tool list, and I’ll generate the project with scripts and a sample Cursor configuration.

- If you already know the specific workflows (e.g., “run pytest and summarize failures”, “create a PR”), share them and I’ll map each to an MCP tool with schemas and guardrails.

---

**User**

My MCP server will be used for code quality. I would also like to use Python for development. Which implementation would you recommend and why?

---

**Cursor**

### Recommendation
- **Python stdio MCP server (local CLI), using the official `mcp` Python package**  
  - Why: Best for code-quality tasks that operate on the local workspace (linters, type-checkers, formatters, tests). Stdio is simple, fast, and secure-by-default on Windows. No networking, trivial to distribute, and easy for Cursor to launch.

### Why this fits code quality
- **Local filesystem access**: Needed for analyzing the user’s repo and respecting local config files.
- **Deterministic tooling**: Works with project venvs and pinned tool versions.
- **Security**: Tight allow-lists and safe roots; no remote attack surface.
- **Performance**: Short-lived processes are fine; add a sidecar daemon only if you need persistent watchers or heavy caching later.

### Suggested initial tool set (Python ecosystem)
- Lint/format:
  - `run_ruff({ paths, fix, select, ignore })`
  - `run_black({ paths, check })`
- Types/tests/security:
  - `run_mypy({ paths, strict })`
  - `run_pytest({ args, report })`
  - `run_bandit({ paths, severity })`
  - `run_safety({ requirements_file })` or `pip-audit`
- VCS and project helpers:
  - `git_diff({ pathspec, staged })`
  - `detect_configs({ tools })` to surface discovered config files
- Utilities:
  - `read_file`, `write_file` (guarded to workspace)
  - `search_in_workspace({ query, glob, limit })`
  - `run_command` with an allow-list (e.g., `["ruff", "black", "mypy", "pytest", "bandit", "pip-audit", "git"]`)

### Resources and subscriptions
- Resources:
  - `file://` under the workspace root
  - Virtual reports: `virtual://lint-report`, `virtual://test-summary`
- Subscriptions:
  - Optional file-change subscription to re-lint on save (debounced)

### Schemas and UX
- Use strict JSON Schemas (`additionalProperties: false`), structured results with:
  - `summary` (counts/severity), `issues` array (file, line, code, message, fixable), `raw` (tool stdout), `durationMs`
- Stream incremental output via notifications for long runs (pytest, mypy).

### Packaging and runtime
- Ship as a Python CLI entry point (e.g., `mcp-code-quality`)
- Detect and prefer the project’s venv (e.g., `.venv`, `poetry env`, `pipenv`)
- Windows-friendly process handling, timeouts, max output size, and cancellation
- Cursor config: add a stdio server entry pointing to your CLI

### When to consider WebSocket or a sidecar
- Add a small **sidecar daemon** if you need persistent watchers, cross-run caches, or background indexing; keep the Cursor-facing process as a thin stdio shim.
- Prefer **WebSocket** only if you must call remote services (org-wide CI, hosted analyzers) or centralize auth; still keep a local stdio server for filesystem tasks.

If you want, I can scaffold this Python stdio server with `mcp`, wire up `ruff`, `black`, and `mypy`, add safe roots, schemas, and a sample Cursor config.

---

**User**

My MCP Server needs to have tools that analyze files, log work done, and manage tasks, is the local stdio server still the best option?

---

**Cursor**

### Short answer
Yes—use a Python stdio MCP server as your primary interface for file analysis, logging, and task management in Cursor. It’s fastest for local file access, simplest to distribute, and secure-by-default on Windows. Add a lightweight local datastore or a sidecar if you need persistence or background jobs.

### Recommended architecture (Python, stdio)
- Local stdio MCP server using `mcp`:
  - Tools for analysis: run local linters, type-checkers, scanners; parse results into structured outputs.
  - Tools for logging: append to a local log store (SQLite/JSONL), and emit `notifications/log` for real-time progress.
  - Tools for tasks: CRUD operations on a local task store (SQLite) with status, timestamps, links to files/runs.
  - Resources: expose `file://` under the workspace; add virtual resources for `virtual://logs/today` and `virtual://tasks/open`.
  - Optional subscriptions: watch file changes and re-run selected analyses (debounced).

### Why stdio fits your needs
- File analysis: direct, low-latency access to the workspace and config files.
- Logging: immediate feedback via MCP notifications, plus durable local storage (SQLite/JSONL).
- Task management: simple local DB gives fast, offline, per-project tasks without auth complexity.
- Operational simplicity: single CLI; no ports, TLS, or tokens required; great Windows support.

### When to add more than stdio
- Add a local sidecar daemon (still local):
  - If you need background indexing, long-running watchers, or caching between runs.
- Consider WebSocket (hybrid) only if:
  - You need shared, multi-user tasks/logs across machines.
  - You must integrate organization services (CI, issue tracker) with central auth.
  - You want a central dashboard for aggregated quality metrics.

### Practical implementation tips
- Storage:
  - Tasks/logs: SQLite (`sqlite3`/`SQLAlchemy`) or append-only JSONL; include rotation and size limits.
  - Include fields: id, type, message, severity, tool, file, line, timestamps, run_id.
- Tool safety:
  - Strict JSON Schemas (`additionalProperties: false`), allow-list external commands, timeouts, max output size, cancellation.
- UX:
  - Return structured results: summary, issues[], raw, durationMs; stream progress via notifications for long tasks.
- Windows:
  - Prefer spawning tools from the project’s venv; handle path quoting; ensure subprocess timeouts and termination.

If you want, I can scaffold the Python stdio server with an embedded SQLite task/log store and example tools (`run_ruff`, `run_mypy`, `log_event`, `task_create/list/update/complete`) plus virtual resources for recent logs and open tasks.

---

**User**

I've decided to use the local stdio server implementation for my MCP server. What would such an implementation look like file hierarchy wise, what files need to be written and developed to get the project started.

---

**Cursor**

### Recommended project layout (Python, stdio MCP server)

```text
mcp-code-quality/
  pyproject.toml
  README.md
  LICENSE
  .gitignore
  .editorconfig
  src/
    mcp_code_quality/
      __init__.py
      server.py              # main MCP server: stdio transport, capabilities
      config.py              # paths, safe roots, allow-lists, timeouts
      logging_setup.py       # structured logging + MCP log notifications
      storage/
        __init__.py
        db.py                # SQLite connection and migrations
        repositories.py      # tasks/logs CRUD
      models/
        __init__.py
        task.py              # Task dataclass / pydantic models
        log_event.py         # Log event models
        results.py           # Normalized analysis result schema
      tools/
        __init__.py
        filesystem.py        # read_file, write_file, search_in_workspace
        ruff.py              # run_ruff tool
        black.py             # run_black tool
        mypy.py              # run_mypy tool
        git.py               # git_diff, maybe git_commit
        commands.py          # run_command (allow-listed)
        tasks.py             # task_create/list/update/complete
        logging_tools.py     # log_event
      resources/
        __init__.py
        files.py             # file:// resource listing/reading
        virtual.py           # virtual://lint-report, virtual://tasks/open
      subscriptions/
        __init__.py
        watchers.py          # optional file-change subscriptions
  tests/
    test_tools.py
    test_storage.py
    test_server.py
```

### Files to create first (MVP)
- pyproject.toml
- src/mcp_code_quality/server.py
- src/mcp_code_quality/config.py
- src/mcp_code_quality/logging_setup.py
- src/mcp_code_quality/tools/{filesystem.py, ruff.py, black.py, mypy.py, tasks.py, logging_tools.py}
- src/mcp_code_quality/resources/{files.py, virtual.py}
- src/mcp_code_quality/storage/{db.py, repositories.py}
- src/mcp_code_quality/models/{task.py, log_event.py, results.py}
- tests/ stubs for quick iteration

### Minimal contents (starter snippets)

- pyproject.toml
```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "mcp-code-quality"
version = "0.1.0"
description = "MCP server for code quality via stdio"
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
  "mcp>=0.1.0",
  "pydantic>=2.8",
  "sqlalchemy>=2.0",
]

[project.scripts]
mcp-code-quality = "mcp_code_quality.server:main"
```

- src/mcp_code_quality/server.py
```python
import asyncio
from mcp.server import Server
from mcp.types import InitializeRequest
from mcp.server.stdio import stdio_server

from .config import ServerConfig, load_config
from .logging_setup import setup_logging
from .tools import filesystem, ruff, black, mypy, tasks, logging_tools
from .resources import files, virtual

def build_server(config: ServerConfig) -> Server:
    server = Server(name="mcp-code-quality", version="0.1.0")

    # Capabilities
    server.set_capabilities(
        tools=True,
        resources=True,
        prompts=False,
        sampling=False,
        logging=True,
        subscriptions=True,
    )

    # Register tools
    filesystem.register(server, config)
    ruff.register(server, config)
    black.register(server, config)
    mypy.register(server, config)
    tasks.register(server, config)
    logging_tools.register(server, config)

    # Register resources
    files.register(server, config)
    virtual.register(server, config)

    return server

def main() -> None:
    config = load_config()
    setup_logging(config)

    server = build_server(config)

    async def run():
        async with stdio_server(server):
            await server.run()

    asyncio.run(run())
```

- src/mcp_code_quality/config.py
```python
from dataclasses import dataclass
from pathlib import Path
from typing import List

@dataclass
class ServerConfig:
    workspace_root: Path
    command_allowlist: List[str]
    subprocess_timeout_sec: int = 120
    max_output_bytes: int = 2_000_000

def load_config() -> ServerConfig:
    # Detect workspace from process CWD (Cursor launches in project root)
    root = Path.cwd()
    return ServerConfig(
        workspace_root=root,
        command_allowlist=["ruff", "black", "mypy", "git", "pytest"],
    )
```

- src/mcp_code_quality/tools/filesystem.py
```python
from mcp.server import Server
from pydantic import BaseModel
from pathlib import Path
from ..config import ServerConfig

class ReadFileParams(BaseModel):
    path: str
    encoding: str = "utf-8"

def register(server: Server, config: ServerConfig) -> None:
    @server.tool("read_file", description="Read a file within the workspace")
    async def read_file(params: ReadFileParams):
        target = (config.workspace_root / params.path).resolve()
        if config.workspace_root not in target.parents and target != config.workspace_root:
            raise ValueError("Path outside workspace root")
        return {"content": target.read_text(encoding=params.encoding)}
```

- src/mcp_code_quality/tools/ruff.py
```python
import asyncio, json
from mcp.server import Server
from pydantic import BaseModel
from ..config import ServerConfig

class RuffParams(BaseModel):
    paths: list[str] = ["."]
    fix: bool = False

def register(server: Server, config: ServerConfig) -> None:
    @server.tool("run_ruff", description="Run ruff linter")
    async def run_ruff(params: RuffParams):
        cmd = ["ruff", "check", "--format", "json"] + (["--fix"] if params.fix else []) + params.paths
        proc = await asyncio.create_subprocess_exec(
            *cmd, cwd=str(config.workspace_root),
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        out, err = await asyncio.wait_for(proc.communicate(), timeout=config.subprocess_timeout_sec)
        results = json.loads(out.decode() or "[]")
        return {"summary": {"issues": len(results)}, "issues": results, "stderr": err.decode()}
```

- src/mcp_code_quality/resources/files.py
```python
from mcp.server import Server
from ..config import ServerConfig

def register(server: Server, config: ServerConfig) -> None:
    @server.resource_list()
    async def list_resources():
        # Expose the workspace root as a discoverable resource root
        return [{"uri": f"file://{config.workspace_root}", "name": "workspace"}]
```

### What this gives you
- A runnable stdio MCP server with clear extension points.
- Safe file access rooted to the workspace.
- First-class code-quality tools (ruff/black/mypy) you can expand.
- A place for durable logs/tasks via SQLite under `storage/` (fill in as you go).
- Clean packaging via `console_scripts` so Cursor can launch `mcp-code-quality`.

If you want, I can generate these files in your workspace with the scaffolding above and stub the remaining modules (tasks/logging/storage) so it runs immediately.

```plaintext
mcp-code-quality/
  pyproject.toml
  README.md
  LICENSE
  .gitignore
  .editorconfig
  src/
    mcp_code_quality/
      __init__.py
      server.py              # main MCP server: stdio transport, capabilities
      config.py              # paths, safe roots, allow-lists, timeouts
      logging_setup.py       # structured logging + MCP log notifications
      storage/
        __init__.py
        db.py                # SQLite connection and migrations
        repositories.py      # tasks/logs CRUD
      models/
        __init__.py
        task.py              # Task dataclass / pydantic models
        log_event.py         # Log event models
        results.py           # Normalized analysis result schema
      tools/
        __init__.py
        filesystem.py        # read_file, write_file, search_in_workspace
        ruff.py              # run_ruff tool
        black.py             # run_black tool
        mypy.py              # run_mypy tool
        git.py               # git_diff, maybe git_commit
        commands.py          # run_command (allow-listed)
        tasks.py             # task_create/list/update/complete
        logging_tools.py     # log_event
      resources/
        __init__.py
        files.py             # file:// resource listing/reading
        virtual.py           # virtual://lint-report, virtual://tasks/open
      subscriptions/
        __init__.py
        watchers.py          # optional file-change subscriptions
  tests/
    test_tools.py
    test_storage.py
    test_server.py
```

```plaintext
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "mcp-code-quality"
version = "0.1.0"
description = "MCP server for code quality via stdio"
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
  "mcp>=0.1.0",
  "pydantic>=2.8",
  "sqlalchemy>=2.0",
]

[project.scripts]
mcp-code-quality = "mcp_code_quality.server:main"
```

```python
import asyncio
from mcp.server import Server
from mcp.types import InitializeRequest
from mcp.server.stdio import stdio_server

from .config import ServerConfig, load_config
from .logging_setup import setup_logging
from .tools import filesystem, ruff, black, mypy, tasks, logging_tools
from .resources import files, virtual

def build_server(config: ServerConfig) -> Server:
    server = Server(name="mcp-code-quality", version="0.1.0")

    # Capabilities
    server.set_capabilities(
        tools=True,
        resources=True,
        prompts=False,
        sampling=False,
        logging=True,
        subscriptions=True,
    )

    # Register tools
    filesystem.register(server, config)
    ruff.register(server, config)
    black.register(server, config)
    mypy.register(server, config)
    tasks.register(server, config)
    logging_tools.register(server, config)

    # Register resources
    files.register(server, config)
    virtual.register(server, config)

    return server

def main() -> None:
    config = load_config()
    setup_logging(config)

    server = build_server(config)

    async def run():
        async with stdio_server(server):
            await server.run()

    asyncio.run(run())
```

```python
from dataclasses import dataclass
from pathlib import Path
from typing import List

@dataclass
class ServerConfig:
    workspace_root: Path
    command_allowlist: List[str]
    subprocess_timeout_sec: int = 120
    max_output_bytes: int = 2_000_000

def load_config() -> ServerConfig:
    # Detect workspace from process CWD (Cursor launches in project root)
    root = Path.cwd()
    return ServerConfig(
        workspace_root=root,
        command_allowlist=["ruff", "black", "mypy", "git", "pytest"],
    )
```

```python
from mcp.server import Server
from pydantic import BaseModel
from pathlib import Path
from ..config import ServerConfig

class ReadFileParams(BaseModel):
    path: str
    encoding: str = "utf-8"

def register(server: Server, config: ServerConfig) -> None:
    @server.tool("read_file", description="Read a file within the workspace")
    async def read_file(params: ReadFileParams):
        target = (config.workspace_root / params.path).resolve()
        if config.workspace_root not in target.parents and target != config.workspace_root:
            raise ValueError("Path outside workspace root")
        return {"content": target.read_text(encoding=params.encoding)}
```

```python
import asyncio, json
from mcp.server import Server
from pydantic import BaseModel
from ..config import ServerConfig

class RuffParams(BaseModel):
    paths: list[str] = ["."]
    fix: bool = False

def register(server: Server, config: ServerConfig) -> None:
    @server.tool("run_ruff", description="Run ruff linter")
    async def run_ruff(params: RuffParams):
        cmd = ["ruff", "check", "--format", "json"] + (["--fix"] if params.fix else []) + params.paths
        proc = await asyncio.create_subprocess_exec(
            *cmd, cwd=str(config.workspace_root),
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        out, err = await asyncio.wait_for(proc.communicate(), timeout=config.subprocess_timeout_sec)
        results = json.loads(out.decode() or "[]")
        return {"summary": {"issues": len(results)}, "issues": results, "stderr": err.decode()}
```

```python
from mcp.server import Server
from ..config import ServerConfig

def register(server: Server, config: ServerConfig) -> None:
    @server.resource_list()
    async def list_resources():
        # Expose the workspace root as a discoverable resource root
        return [{"uri": f"file://{config.workspace_root}", "name": "workspace"}]
```

