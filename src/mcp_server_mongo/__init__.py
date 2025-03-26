from . import server


def main():
    """Main entry point for the package."""
    # 如果指定了从环境变量读取，且环境变量存在，则使用环境变量中的值
    server.mcp.run(transport="stdio")


# Optionally expose other important items at package level
__all__ = ["main", "server"]
