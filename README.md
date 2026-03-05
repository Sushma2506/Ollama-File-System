# 🤖 Local AI Agent using MCP + Ollama

A privacy-first AI agent that runs **completely on your local machine** — no data sent to any external server. Built using the Model Context Protocol (MCP) and Ollama for local LLM inference.

## What This Does

This project turns a local LLM (via Ollama) into an **AI agent** that can interact with your filesystem. You can chat with it naturally and it will perform file operations on your behalf — with your explicit permission every time.

**Example queries:**
- `list all directories in my Documents folder`
- `create a file named notes.txt in Documents with content "hello world"`
- `read the file at Documents/notes.txt`
- `search for files named test in my home folder`

## How It Works

```
You (chat input)
      ↓
Python Host (host.py)
      ↓
Ollama (local LLM - llama3.1) → decides which tool to use
      ↓
Human-in-the-Loop (YOU approve/deny every action)
      ↓
MCP Filesystem Server (executes the tool)
      ↓
Result → back to Ollama → final answer to you
```

## Architecture

| Component | Technology |
|-----------|-----------|
| MCP Host | Python (custom built) |
| LLM | Ollama (llama3.1) |
| MCP Server | @modelcontextprotocol/server-filesystem |
| Transport | STDIO (local) |
| Privacy | 100% local — nothing leaves your PC |

## Available Tools

The filesystem MCP server exposes these tools:
- `read_file` — read file contents
- `write_file` — create or write to a file
- `edit_file` — edit existing files
- `list_directory` — list contents of a directory
- `create_directory` — create a new folder
- `move_file` — move or rename files
- `search_files` — search for files by name
- `get_file_info` — get metadata about a file
- `directory_tree` — view folder structure
- `list_allowed_directories` — see accessible directories

## Prerequisites

- Python 3.10+
- Node.js and npm (for MCP filesystem server)
- [Ollama](https://ollama.ai) installed and running
- llama3.1 model pulled in Ollama

## Installation

**1. Clone the repository:**
```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

**2. Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**3. Install Ollama and pull the model:**
```bash
ollama pull llama3.1
```

**4. Configure your allowed directory:**

Open `host.py` and update the path in `connect_to_server()`:
```python
args=[
    "-y",
    "@modelcontextprotocol/server-filesystem",
    "/your/desired/directory",  # change this to your path
],
```

## Usage

```bash
python host.py
```

You will see:
```
Connected to server with tools: ['read_file', 'write_file', ...]
MCP Client Started!
Type your queries or 'quit' to exit.

Query: 
```

Type your query and the agent will:
1. Decide which tool to use
2. **Ask your permission before doing anything (HIL)**
3. Execute only if you approve
4. Return the result

Type `quit` to exit.

## Security

This agent is built with security in mind:

- **Human-in-the-Loop (HIL)** — every tool call requires your explicit `allow` or `deny` before executing
- **Local only** — everything runs on your machine, no external API calls
- **STDIO transport** — uses local process communication, not HTTP
- **You control the scope** — only the directories you configure are accessible

## Requirements

```
ollama
mcp
```

Install with:
```bash
pip install -r requirements.txt
```

## Project Structure

```
your-repo/
├── host.py           # Main MCP host and agent logic
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## What I Learned Building This

- Model Context Protocol (MCP) architecture — hosts, clients, servers
- How to build an AI agent from scratch without frameworks
- STDIO vs HTTP transport in MCP
- Human-in-the-Loop (HIL) security patterns
- Integrating local LLMs (Ollama) with MCP
- Async Python programming with asyncio
- Why local LLMs are better for privacy than cloud APIs

## Future Enhancements

- [ ] Conversation history (remember previous queries)
- [ ] Voice control input
- [ ] Support for multiple MCP servers
- [ ] Better error handling
- [ ] Web UI
