# MCP Code Quality Server - Project Plan

## What is MCP?

- **Model Context Protocol (MCP)** is an open, transport-agnostic protocol for connecting AI clients (e.g., IDEs, chat apps, agents) to external tools and data sources via standardized JSON-RPC methods.
- It cleanly separates roles:
  - **Client**: UI/agent that hosts the model and orchestrates calls
  - **Server**: Exposes tools, data resources, and prompts the model can use
- Built to be simple, secure-by-default, and composable across transports like stdio and WebSocket

## MCP in Python

- In Python, it's just a small async stdio app that registers tools and resources and runs in the background waiting for communication from an AI IDE/assistant
- **Tools**: Functions and features
- **Resources**: Files and data sources

## Can Tools Have Subtools?

**No** - Tools cannot have subtools. Instead, you can either:
- Create separate tools that work together, or
- Create tools with complex parameters

## MCP Server Implementation Options

### 1. Local stdio server (Recommended for dev tools)
- Cursor launches your server as a child process and communicates over stdio
- Best for file-system tools, build/test runners, linters, git, and other local actions
- Simple to distribute (just a CLI). Good security by OS permissions and explicit allow-listing

### 2. Local/remote WebSocket server
- Cursor connects to ws:// or wss:// URL
- Good when tools live in a service (CI, issues, docs, internal APIs)
- Add auth (token/mTLS) at the transport layer

### 3. Hybrid (stdio + remote)
- A local stdio server exposes local tools and also proxies selected remote APIs
- Keeps secrets in one place; centralizes rate-limiting and caching

### 4. Sidecar daemon + stdio shim
- Long-lived daemon maintains watchers, caches, sessions
- A thin stdio process is launched by Cursor and relays to the daemon
- Useful for fast file-change subscriptions and persistent auth flows

**Recommendation**: Option 1 (Local stdio server) is the best fit for a 'code quality' implementation because it:
- Has access to file system
- Simple to distribute
- Secured-by-default on Windows

## MCP Server Requirements

### Tools to Implement

#### 1. Analyze Files Tool
- **Line counting** (required) - relative file path in project directory
- **String searches** for TODO, function keywords, comments

#### 2. Work Logging Tool
- Append-only log of what you worked on
- Basic timestamp and description

#### 3. Task Management Tool
- Add, list, and mark tasks as complete
- Choose your storage approach
- Impressive if fully implemented

## Tool Specifications

### Analyze Files Tool

**Parameters**: 
- `file_path` (relative file path from project directory root)
- `option` (analysis type)

**Options**:
- **Line Counter**: Counts the number of lines in a file and returns them
- **hasTodos**: Determines if a file has a comment containing the case sensitive string 'TODO', usually indicative of an unfinished code block and returns a bool

### Work Logging Tool

**Parameters**:
- `description` (description of work performed)

**Functionality**: Keeps track of work in an append-only log with description of work and timestamp of append

### Task Manager Tool

**Parameters**: TBD

**Functionality**: TBD

## Project TODO List

- [x] Get a barebones server running, establish communication between MCP server and AI model
- [x] Test a simple 'echo' tool to confirm communication
- [ ] Create first tool, analyze files
- [ ] Test analyze files tool, edge cases, error handling