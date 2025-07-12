# Listmonk MCP Server Setup

Configuration guides for adding the Listmonk MCP server to various IDEs and AI assistants.

## Setup Guides

Choose your preferred environment:

- **[Claude Desktop](./claude-desktop.md)** - Claude Desktop app configuration
- **[VS Code](./vscode.md)** - VS Code MCP settings  
- **[Cline](./cline.md)** - Cline extension configuration
- **[Windsurf & Cursor](./windsurf-cursor.md)** - Windsurf and Cursor IDE setup

## Common Configuration

All setups use the same basic configuration format:

```json
{
  "command": "uv",
  "args": ["run", "python", "-m", "listmonk_mcp.server"],
  "cwd": "/path/to/listmonk-mcp",
  "env": {
    "LISTMONK_MCP_URL": "http://localhost:9000",
    "LISTMONK_MCP_USERNAME": "your-api-username", 
    "LISTMONK_MCP_PASSWORD": "your-api-token"
  }
}
```

## Prerequisites

1. Install project: `git clone https://github.com/rhnvrm/listmonk-mcp.git`
2. Create API user and token in Listmonk Admin → Users
3. Configure environment variables for your chosen IDE