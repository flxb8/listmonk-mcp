# Windsurf & Cursor Setup

Add the Listmonk MCP server to Windsurf or Cursor IDEs.

## Windsurf Configuration

Add to your Windsurf MCP settings:

```json
{
  "mcpServers": {
    "listmonk": {
      "command": "uv",
      "args": ["run", "python", "-m", "listmonk_mcp.server"],
      "cwd": "/path/to/listmonk-mcp",
      "env": {
        "LISTMONK_MCP_URL": "http://localhost:9000",
        "LISTMONK_MCP_USERNAME": "your-api-username",
        "LISTMONK_MCP_PASSWORD": "your-api-token"
      }
    }
  }
}
```

## Cursor Configuration

Add to your Cursor MCP settings:

```json
{
  "mcpServers": {
    "listmonk": {
      "command": "uv",
      "args": ["run", "python", "-m", "listmonk_mcp.server"],
      "cwd": "/path/to/listmonk-mcp",
      "env": {
        "LISTMONK_MCP_URL": "http://localhost:9000",
        "LISTMONK_MCP_USERNAME": "your-api-username",
        "LISTMONK_MCP_PASSWORD": "your-api-token"
      }
    }
  }
}
```

## Environment Variables

- `LISTMONK_MCP_URL`: Your Listmonk server URL
- `LISTMONK_MCP_USERNAME`: API user created in Admin → Users
- `LISTMONK_MCP_PASSWORD`: API token (not user password)

## Prerequisites

1. Install the project: `git clone https://github.com/rhnvrm/listmonk-mcp.git`
2. Create API user and token in Listmonk admin interface
3. Restart your IDE after adding configuration