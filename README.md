# know: A simple MCP knowledge base

This MCP server adds to tools to your agent:

1. `search_project_docs` performs semantic search through your project's knowledge base (default `docs/` directory)
2. `store_project_docs` adds a new document to the project's knowledge base and indexes it.

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
    "project-docs-mcp": {
      "type": "local",
      "command": ["uvx", "project-docs", "mcp"]
    }
  }
}
```

## Configure

Can be configured through environment variables

- `PROJECT_DOCS_PATH` (default `docs/`): Where are markdown documents with the relevant information.
- `PROJECT_DOCS_INDEX_FILE` (default `.project-docs.idx`): Where to store the binary index.
- `PROJECT_DOCS_TOC_FILE` (default `.project-docs-toc.json`): name of a JSON file that stores the relationship between vectors in the index and files on disc.
