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

**Recommendation**: Option 1 (Local stdio server) is the best fit for implementation because it:
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
- `file_path` (relative file path from project directory root) (required)
- `option` (analysis option) (required)

**Functionality**:
  **Options**:
  - **`lineCount`**: Counts the number of lines in a file and returns them
  - **`hasTodos`**: Determines if a file has a comment containing the case sensitive string 'TODO', usually indicative of an unfinished code block and returns a bool

### Work Logging Tool

**Parameters**:
- `description` (description of work performed)

**Functionality**: Keeps track of work in an append-only log with description of work and timestamp of append

### Get Work Log Tool

**Parameters**:
- none

**Functionality**: Returns the append-only work log

### Task Manager Tool

**Parameters**:
- `option` (task management option) (required)
- `taskName` (name of task) (required when option parameter is `addTask` or `completeTask`)
- `description` (description of task) (required when option parameter is `addTask`)
- `completionStatus` (a value of either `complete` or `not complete`) (required when option parameter is `completeTask`)

**Functionality**:
  **Options**:
  - **`addTask`**: adds a task (name, description, completionStatus (complete or not complete)) to the collection of tasks
  - **`listTasks`**: lists out all the tasks and their attributes from the collection of tasks
  - **`completeTask`**: edits completion status for selected task via taskName parameter

**Storage**:
  **Comparison Summary**:
| Feature | Plain Text | JSON File | SQLite |
|---------|------------|-----------|---------|
| Complexity | Low | Medium | Medium-High |
| Data Structure | None | Good | Excellent |
| Querying | Manual | Basic | Full SQL |
| Concurrency | Poor | Fair | Excellent |
| Human Readable | Yes | Yes | No |

- SQLite option provides advanced querying capabilities while providing a base for future features

## Project TODO List

- [x] Get a barebones server running, establish communication between MCP server and AI model
- [x] Test MCP server communication with simple echo tool
- [x] Create first tool, analyze files
- [x] Test analyze files tool, edge cases, error handling, unit testing, manual testing
- [x] Create work logging tool, logWork
- [x] Test work logging tool, edge cases, error handling, unit testing, manual testing
- [x] Create get work log tool, getWorkLog
- [x] Test get work log tool, edge cases, error handling, unit testing, manual testing
- [x] Create Task manager tool, taskManager
- [x] Test Task manager tool, edge cases, error handling, unit testing, manual testing

## What are AI Agents?

AI agents are autonomous software entities that can perceive their environment, make decisions, and take actions to achieve specific goals. They operate with varying levels of autonomy and can be designed for specific tasks or general problem-solving.

## AI Models vs AI Agents

### AI Models (like LLMs)
- **What they are**: Computational systems trained on data to perform specific tasks
- **Core function**: Process inputs and generate outputs
- **Examples**: GPT, BERT, ResNet, etc.
- **Nature**: Stateless, reactive components

### AI Agents
- **What they are**: Systems that use AI models (and other tools) to achieve goals
- **Core function**: Plan, decide, and act autonomously
- **Examples**: Autonomous robots, trading bots, personal assistants
- **Nature**: Stateful, proactive systems

## Key Differences

| Aspect | AI Models | AI Agents |
|--------|-----------|-----------|
| Purpose | Process data/inputs | Achieve goals |
| State | Stateless | Stateful |
| Behavior | Reactive | Proactive + Reactive |
| Autonomy | None | High |
| Decision Making | Pattern matching | Goal-oriented planning |
| Tools | Input → Output | Can use multiple tools/models |

## Summary

AI models (like LLMs) are the "brain" that processes information, while AI agents are the "body" that uses that brain to achieve goals. For code quality improvements, you'll typically want to build agents that use LLMs as one of their tools, rather than just using LLMs directly. This gives you the autonomy, planning, and learning capabilities needed for effective code quality management.