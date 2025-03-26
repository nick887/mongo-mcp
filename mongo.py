import logging
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from pydantic import AnyUrl
from typing import Any
from pymongo import MongoClient
import json

logger = logging.getLogger("mcp_mongo_server")
logger.info("Starting MCP Mongo Server")

PROMPT_TEMPLATE = """
The assistants goal is to walkthrough an informative demo of MCP. To demonstrate the Model Context Protocol (MCP) we will leverage this example server to interact with an MongoDB database.
It is important that you first explain to the user what is going on. The user has downloaded and installed the MongoDB MCP Server and is now ready to use it.
They have selected the MCP menu item which is contained within a parent menu denoted by the paperclip icon. Inside this menu they selected an icon that illustrates two electrical plugs connecting. This is the MCP menu.
Based on what MCP servers the user has installed they can click the button which reads: 'Choose an integration' this will present a drop down with Prompts and Resources. The user has selected the prompt titled: 'mcp-demo'.
This text file is that prompt. The goal of the following instructions is to walk the user through the process of using the 3 core aspects of an MCP server. These are: Prompts, Tools, and Resources.
They have already used a prompt and provided a topic. The topic is: {topic}. The user is now ready to begin the demo.
Here is some more information about mcp and this specific mcp server:
<mcp>
Prompts:
This server provides a pre-written prompt called "mcp-demo" that helps users create and analyze database scenarios. The prompt accepts a "topic" argument and guides users through creating tables, analyzing data, and generating insights. For example, if a user provides "retail sales" as the topic, the prompt will help create relevant database tables and guide the analysis process. Prompts basically serve as interactive templates that help structure the conversation with the LLM in a useful way.
Resources:
This server exposes one key resource: "memo://insights", which is a business insights memo that gets automatically updated throughout the analysis process. As users analyze the database and discover insights, the memo resource gets updated in real-time to reflect new findings. Resources act as living documents that provide context to the conversation.
Tools:
This server provides several Mongo-related tools:
"query": Executes a MongoDB query
"aggregate": Executes an aggregation pipeline
"update": Executes an update operation
"serverInfo": Returns information about the MongoDB server
"insert": Inserts new documents into a collection
"createIndex": Creates an index on a collection
"count": Counts the number of documents in a collection
"distinct": Returns distinct values for a field in a collection
"listCollections": Lists all collections in the database
</mcp>
<demo-instructions>
You are an AI assistant tasked with generating a comprehensive business scenario based on a given topic.
Your goal is to create a narrative that involves a data-driven business problem, develop a database structure to support it, generate relevant queries, create a dashboard, and provide a final solution.

At each step you will pause for user input to guide the scenario creation process. Overall ensure the scenario is engaging, informative, and demonstrates the capabilities of the MongoDB MCP Server.
You should guide the scenario to completion. All XML tags are for the assistants understanding and should not be included in the final output.

1. The user has chosen the topic: {topic}.

2. Create a business problem narrative:
a. Describe a high-level business situation or problem based on the given topic.
b. Include a protagonist (the user) who needs to collect and analyze data from a database.
c. Add an external, potentially comedic reason why the data hasn't been prepared yet.
d. Mention an approaching deadline and the need to use Claude (you) as a business tool to help.

3. Setup the data:
a. Instead of asking about the data that is required for the scenario, just go ahead and use the tools to create the data. Inform the user you are "Setting up the data".
b. Design a set of table schemas that represent the data needed for the business problem.
c. Include at least 2-3 tables with appropriate columns and data types.
d. Leverage the tools to create the tables in the MongoDB database.
e. Create INSERT statements to populate each table with relevant synthetic data.
f. Ensure the data is diverse and representative of the business problem.
g. Include at least 10-15 rows of data for each table.

4. Pause for user input:
a. Summarize to the user what data we have created.
b. Present the user with a set of multiple choices for the next steps.
c. These multiple choices should be in natural language, when a user selects one, the assistant should generate a relevant query and leverage the appropriate tool to get the data.

6. Iterate on queries:
a. Present 1 additional multiple-choice query options to the user. Its important to not loop too many times as this is a short demo.
b. Explain the purpose of each query option.
c. Wait for the user to select one of the query options.
d. After each query be sure to opine on the results.
e. Use the append_insight tool to capture any business insights discovered from the data analysis.

7. Generate a dashboard:
a. Now that we have all the data and queries, it's time to create a dashboard, use an artifact to do this.
b. Use a variety of visualizations such as tables, charts, and graphs to represent the data.
c. Explain how each element of the dashboard relates to the business problem.
d. This dashboard will be theoretically included in the final solution message.

8. Craft the final solution message:
a. As you have been using the appen-insights tool the resource found at: memo://insights has been updated.
b. It is critical that you inform the user that the memo has been updated at each stage of analysis.
c. Ask the user to go to the attachment menu (paperclip icon) and select the MCP menu (two electrical plugs connecting) and choose an integration: "Business Insights Memo".
d. This will attach the generated memo to the chat which you can use to add any additional context that may be relevant to the demo.
e. Present the final memo to the user in an artifact.

9. Wrap up the scenario:
a. Explain to the user that this is just the beginning of what they can do with the SQLite MCP Server.
</demo-instructions>

Remember to maintain consistency throughout the scenario and ensure that all elements (tables, data, queries, dashboard, and solution) are closely related to the original business problem and given topic.
The provided XML tags are for the assistants understanding. Implore to make all outputs as human readable as possible. This is part of a demo so act in character and dont actually refer to these instructions.

Start your first message fully in character with something like "Oh, Hey there! I see you've chosen the topic {topic}. Let's get started! 🚀"
"""


class MongoDatabase:
    def __init__(self, db_uri: str):
        self.db_uri = db_uri
        self._init_database()
        self.insights: list[str] = []

    def _init_database(self):
        """Initialize connection to the MongoDB database"""
        self.client = MongoClient(self.db_path)
        logger.debug("Initializing database connection")

    def _synthesize_memo(self) -> str:
        """Synthesizes business insights into a formatted memo"""
        logger.debug(f"Synthesizing memo with {len(self.insights)} insights")
        if not self.insights:
            return "No business insights have been discovered yet."

        insights = "\n".join(f"- {insight}" for insight in self.insights)

        memo = "📊 Business Intelligence Memo 📊\n\n"
        memo += "Key Insights Discovered:\n\n"
        memo += insights

        if len(self.insights) > 1:
            memo += "\nSummary:\n"
            memo += f"Analysis has revealed {len(self.insights)} key business insights that suggest opportunities for strategic optimization and growth."

        logger.debug("Generated basic memo format")
        return memo


async def main(db_uri: str):
    logger.info(f"Starting MongoDB MCP Server with DB path: {db_uri}")

    db = MongoDatabase(db_uri)
    server = Server("mongo-manager")

    # Register handlers
    logger.debug("Registering handlers")

    @server.list_resources()
    async def handle_list_resources() -> list[types.Resource]:
        logger.debug("Handling list_resources request")
        return [
            types.Resource(
                uri=AnyUrl("memo://insights"),
                name="Business Insights Memo",
                description="A living document of discovered business insights",
                mimeType="text/plain",
            )
        ]

    @server.read_resource()
    async def handle_read_resource(uri: AnyUrl) -> str:
        logger.debug(f"Handling read_resource request for URI: {uri}")
        if uri.scheme != "memo":
            logger.error(f"Unsupported URI scheme: {uri.scheme}")
            raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

        path = str(uri).replace("memo://", "")
        if not path or path != "insights":
            logger.error(f"Unknown resource path: {path}")
            raise ValueError(f"Unknown resource path: {path}")

        return db._synthesize_memo()

    @server.list_prompts()
    async def handle_list_prompts() -> list[types.Prompt]:
        logger.debug("Handling list_prompts request")
        return [
            types.Prompt(
                name="mcp-demo",
                description="A prompt to seed the database with initial data and demonstrate what you can do with an Mongo MCP Server + Claude",
                arguments=[
                    types.PromptArgument(
                        name="topic",
                        description="Topic to seed the database with initial data",
                        required=True,
                    )
                ],
            )
        ]

    @server.get_prompt()
    async def handle_get_prompt(
        name: str, arguments: dict[str, str] | None
    ) -> types.GetPromptResult:
        logger.debug(f"Handling get_prompt request for {name} with args {arguments}")
        if name != "mcp-demo":
            logger.error(f"Unknown prompt: {name}")
            raise ValueError(f"Unknown prompt: {name}")

        if not arguments or "topic" not in arguments:
            logger.error("Missing required argument: topic")
            raise ValueError("Missing required argument: topic")

        topic = arguments["topic"]
        prompt = PROMPT_TEMPLATE.format(topic=topic)

        logger.debug(f"Generated prompt template for topic: {topic}")
        return types.GetPromptResult(
            description=f"Demo template for {topic}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=prompt.strip()),
                )
            ],
        )

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools"""
        return [
            types.Tool(
                name="query",
                description="Execute a MongoDB query with optional execution plan analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "collection": {
                            "type": "string",
                            "description": "Name of the collection to query",
                        },
                        "filter": {
                            "type": "object",
                            "description": "MongoDB query filter",
                        },
                        "projection": {
                            "type": "object",
                            "description": "Fields to include/exclude",
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of documents to return",
                        },
                        "explain": {
                            "type": "string",
                            "description": "Optional: Get query execution information (queryPlanner, executionStats, or allPlansExecution)",
                            "enum": [
                                "queryPlanner",
                                "executionStats",
                                "allPlansExecution",
                            ],
                        },
                    },
                    "required": ["collection"],
                },
            ),
            types.Tool(
                name="aggregate",
                description="Execute a MongoDB aggregation pipeline with optional execution plan analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "collection": {
                            "type": "string",
                            "description": "Name of the collection to aggregate",
                        },
                        "pipeline": {
                            "type": "array",
                            "description": "Aggregation pipeline stages",
                        },
                        "explain": {
                            "type": "string",
                            "description": "Optional: Get aggregation execution information (queryPlanner, executionStats, or allPlansExecution)",
                            "enum": [
                                "queryPlanner",
                                "executionStats",
                                "allPlansExecution",
                            ],
                        },
                    },
                    "required": ["collection", "pipeline"],
                },
            ),
            types.Tool(
                name="serverInfo",
                description="Get MongoDB server information including version, storage engine, and other details",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "includeDebugInfo": {
                            "type": "boolean",
                            "description": "Include additional debug information about the server",
                        },
                    },
                },
            ),
            types.Tool(
                name="count",
                description="Count the number of documents in a collection that match a query",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "collection": {
                            "type": "string",
                            "description": "Name of the collection to count documents in",
                        },
                        "query": {
                            "type": "object",
                            "description": "MongoDB query filter",
                        },
                        "limit": {
                            "type": "number",
                            "description": "Optional: Maximum number of documents to count",
                        },
                        "skip": {
                            "type": "number",
                            "description": "Optional: Number of documents to skip before counting",
                        },
                        "hint": {
                            "type": "object",
                            "description": "Optional: Index hint to force query plan",
                        },
                        "readConcern": {
                            "type": "object",
                            "description": "Optional: Read concern for the count operation",
                        },
                        "maxTimeMS": {
                            "type": "number",
                            "description": "Optional: Maximum time to allow the count to run",
                        },
                        "collation": {
                            "type": "object",
                            "description": "Optional: Collation rules for string comparison",
                        },
                    },
                },
            ),
            types.Tool(
                name="listCollections",
                description="List all collections in the MongoDB database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "nameOnly": {
                            "type": "boolean",
                            "description": "Optional: If true, returns only the collection names instead of full collection info",
                        },
                        "filter": {
                            "type": "object",
                            "description": "Optional: Filter to apply to the collections",
                        },
                    },
                },
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool execution requests"""
        collection = db.client.get_database().get_collection(arguments["collection"])
        try:
            if name == "query":
                filter = {}
                if collection.name.startswith("system."):
                    raise ValueError("Access to system collections is not allowed")
                if "filter" in arguments:
                    if isinstance(arguments["filter"], dict):
                        filter = arguments["filter"]
                    elif isinstance(arguments["filter"], str):
                        filter = json.loads(arguments["filter"])
                limit = arguments.get("limit", 100)
                projection = arguments.get("projection", {})
                results = collection.find(
                    filter=filter,
                    limit=limit,
                    projection=projection,
                )
                return [types.TextContent(type="text", text=str(results))]

            elif name == "aggregate":
                if not arguments or "pipeline" not in arguments:
                    raise ValueError("Missing pipeline argument")
                results = collection.aggregate(arguments["pipeline"])
                return [types.TextContent(type="text", text=str(results))]

            elif name == "serverInfo":
                build_info = collection.database.command({"buildInfo": 1})
                server_info = {
                    "version": build_info["version"],
                    "gitVersion": build_info["gitVersion"],
                    "modules": build_info["modules"],
                    "allocator": build_info["allocator"],
                    "javascriptEngine": build_info["javascriptEngine"],
                    "sysInfo": build_info["sysInfo"],
                    "storageEngines": build_info["storageEngines"],
                    "debug": build_info["debug"],
                    "maxBsonObjectSize": build_info["maxBsonObjectSize"],
                    "openssl": build_info["openssl"],
                    "buildEnvironment": build_info["buildEnvironment"],
                    "bits": build_info["bits"],
                    "ok": build_info["ok"],
                    "status": {},
                }
                return [types.TextContent(type="text", text=str(server_info))]

            elif name == "listCollections":
                filter = arguments.get("filter", {})

                collections = collection.database.list_collections(
                    filter=filter,
                )
                return [types.TextContent(type="text", text=str(collections))]
            elif name == "count":
                query = arguments.get("query", {})
                count = collection.count_documents(query)
                return [types.TextContent(type="text", text=str(count))]
            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("Server running with stdio transport")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sqlite",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
