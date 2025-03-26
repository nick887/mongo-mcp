# MCP Server for MongoDB

A MongoDB MCP (Model-Controller-Proxy) server that supports read-only operations. This server can be safely integrated with Cursor IDE, allowing MongoDB database queries through the MCP protocol.

## Features

- Read-only operations for enhanced database security
- Support for basic MongoDB query operations
- Seamless integration with Cursor IDE
- Compatible with Python 3.9 and above

## Installation

1. Ensure Python 3.9 or higher is installed on your system
2. Clone this repository:
   ```bash
   git clone https://github.com/nick887/mongo-mcp.git
   cd mongo-mcp
   ```
3. Install dependencies using uv:
   ```bash
   uv venv
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate  # Windows
   uv pip install -e .
   ```

## Configuration

### Cursor MCP Configuration

Add the following MCP configuration to your Cursor settings:

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
          "db_uri": "mongodb://your-mongodb-connection-string"
        }
      }
    }
}
```

Configuration notes:
- `/PATH/TO/mongo-mcp`: Replace with your actual project path
- `db_uri`: Replace with your MongoDB connection string

## Supported Operations

The server supports the following MongoDB read-only operations:
- Document queries (find)
- Aggregation operations (aggregate)
- Count operations (count)
- Server information retrieval (serverInfo)
- Collection listing (listCollections)

## Security Notes

- This server only supports read operations; write, update, and delete operations are not supported
- It is recommended to use a database user with read-only privileges
- Ensure database connection strings are not hardcoded in the source code

## License

This project is licensed under the Apache License 2.0 - see below for details:

```
Copyright 2025 nick887

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## Contributing

Issues and Pull Requests are welcome!

