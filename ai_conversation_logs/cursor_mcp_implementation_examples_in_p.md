# MCP implementation examples in Python
_Exported on 9/24/2025 at 13:57:57 PDT from Cursor (1.6.45)_

---

**User**

What does MCP look like in action using python?

---

**Cursor**

```json
{
  "mcpServers": {
    "python-echo": {
      "command": "python",
      "args": ["C:/path/server.py"],
      "env": {}
    }
  }
}
```

### Short answer
MCP (Model Context Protocol) lets you expose tools and resources from a local “server” process that your AI IDE/assistant (like Cursor or Claude) can call. In Python, it’s just a small async stdio app that registers tools and runs.

### Minimal Python MCP server (runnable)
1) Install
```bash
pip install mcp
```

2) Create `server.py`
```python
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent

server = Server("python-echo")

@server.tool("echo", "Echo back the provided text")
async def echo(text: str) -> list[TextContent]:
    return [TextContent(type="text", text=f"You said: {text}")]

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write)

if __name__ == "__main__":
    asyncio.run(main())
```

3) Run (for manual test)
```bash
python server.py
```
This waits on stdio for an MCP client (like Cursor/Claude) to connect.

### Hook it up in Cursor (Windows)
Add an entry to your `.cursor/mcp.json` so Cursor can auto-launch the server when needed:
```json
{
  "mcpServers": {
    "python-echo": {
      "command": "python",
      "args": ["C:/Users/Administrator/Desktop/AI Workspace/AI-Coding-Challenge/server.py"],
      "env": {}
    }
  }
}
```

Then, in Cursor’s chat, you’ll see the `python-echo` server available. Ask the assistant to use the `echo` tool, e.g., “Use the echo tool with text = hello,” and you’ll get “You said: hello” returned from your Python MCP server.

### Optional: add a simple resource
```python
from mcp.types import Resource, TextResourceContents

@server.list_resources()
async def list_resources():
    return [Resource(uri="demo://hello", name="Hello", mimeType="text/plain")]

@server.read_resource()
async def read_resource(uri: str):
    if uri == "demo://hello":
        return [TextResourceContents(uri=uri, text="Hello from MCP")]
    raise FileNotFoundError("Unknown resource")
```
Now clients can list and read `demo://hello` via MCP.

- **Result**: You’ve seen MCP “in action” in Python: a tiny async server that exposes a tool (and optionally a resource) over stdio, launched by your IDE and callable from chat.

```shellscript
pip install mcp
```

```python
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent

server = Server("python-echo")

@server.tool("echo", "Echo back the provided text")
async def echo(text: str) -> list[TextContent]:
    return [TextContent(type="text", text=f"You said: {text}")]

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write)

if __name__ == "__main__":
    asyncio.run(main())
```

```shellscript
python server.py
```

```json
{
  "mcpServers": {
    "python-echo": {
      "command": "python",
      "args": ["C:/Users/Administrator/Desktop/AI Workspace/AI-Coding-Challenge/server.py"],
      "env": {}
    }
  }
}
```

```python
from mcp.types import Resource, TextResourceContents

@server.list_resources()
async def list_resources():
    return [Resource(uri="demo://hello", name="Hello", mimeType="text/plain")]

@server.read_resource()
async def read_resource(uri: str):
    if uri == "demo://hello":
        return [TextResourceContents(uri=uri, text="Hello from MCP")]
    raise FileNotFoundError("Unknown resource")
```

---