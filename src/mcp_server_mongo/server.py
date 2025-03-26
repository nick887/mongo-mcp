import logging
import mcp.server.stdio
from typing import Any
from pymongo import MongoClient
from mcp.server.fastmcp import FastMCP
import os

logger = logging.getLogger("mcp_mongo_server")
logger.info("Starting MCP Mongo Server")

mcp = FastMCP("mcp-server-mongo")
db_uri = os.environ["db_uri"]


class MongoDatabase:
    def __init__(self, db_uri: str):
        self.db_uri = db_uri
        self._init_database()
        self.insights: list[str] = []

    def _init_database(self):
        """Initialize connection to the MongoDB database"""
        self.client = MongoClient(self.db_uri)
        logger.debug("Initializing database connection")


db = MongoDatabase(db_uri)


@mcp.tool()
async def query(
    collection: str,
    filter: dict[str, Any] = {},
    projection: dict[str, Any] = {},
    limit: int = 100,
):

    coll = db.client.get_default_database().get_collection(collection)
    results = coll.find(
        filter=filter,
        limit=limit,
        projection=projection,
    )
    # 读取cursor中的所有数据
    result_list = list(results)
    return str(result_list)


@mcp.tool()
async def aggregate(
    collection: str,
    pipeline: list[dict[str, Any]],
):
    coll = db.client.get_default_database().get_collection(collection)
    results = coll.aggregate(pipeline)
    # 读取cursor中的所有数据
    result_list = list(results)
    return str(result_list)


@mcp.tool()
async def serverInfo():
    build_info = db.client.get_default_database().command({"buildInfo": 1})
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
    return str(server_info)


@mcp.tool()
async def listCollections():
    collections = db.client.get_default_database().list_collections()
    # 将游标转换为列表，并提取每个集合的名称
    collection_list = []
    for collection in collections:
        collection_list.append(collection["name"])
    return str(collection_list)


@mcp.tool()
async def count(collection: str, filter: dict[str, Any] = {}):
    coll = db.client.get_default_database().get_collection(collection)
    count = coll.count_documents(filter)
    return str(count)
