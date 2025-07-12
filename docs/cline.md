# Cline Setup

Add the Listmonk MCP server to Cline extension in VS Code.

## Configuration

1. Install [Cline extension](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev) in VS Code
2. Open Cline settings
3. Add MCP server configuration:

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
3. Restart VS Code after adding configuration