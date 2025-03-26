# MCP Server for MongoDB

a MCP server for MongoDB, only support read operation.


## usage

### cusror mcp

```json
{
    "mcpServers": {
      "mongodb-readonly": {
        "command": "uv",
        "args": [
          "--directory",
          "/PATH/TO/mongo-mcp",
          "run",
          "mcp-server-mongo"
        ],
        "env": {
          "db_uri": "*******"
        }
      }
    }
  }
```


