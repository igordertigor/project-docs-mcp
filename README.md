# know: A simple MCP knowledge base

This MCP server adds to tools to your agent:

1. `search_project_knowledge` performs semantic search through your project's knowledge base (default `docs/` directory)
2. `store_project_knowledge` adds a new document to the project's knowledge base and indexes it.

## Getting started

Create a knowledge directory
```py
mkdir -p docs/
```
Add mcp server (e.g. for opencode):
```txt
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "know": {
      "type": "local",
      "command": ["uv", "run", "know", "mcp"]
    }
  }
}
```

## Configure

Can be configured through environment variables

- `KNOWLEDGE_PATH` (default `docs/`): Where are markdown documents with the relevant information.
- `KNOWLEDGE_INDEX_FILE` (default `.knowledge`): Where to store the binary index.
- `KNOWLEDGE_TOC` (default `.knowledge-toc`): name of a json file that stores the relationship between vectors in the index and files on disc
