"""
Entry point for FastMCP Cloud deployment.
This file ONLY exports the mcp instance without any initialization code.
"""

# Import the mcp instance from server.py
# This will trigger module-level initialization (database, etc.)
# but will NOT call mcp.run() because that's only in if __name__ == "__main__"
from .server import mcp

# That's it! FastMCP Cloud will use this mcp object directly.
# No main() function, no mcp.run(), no event loop conflicts.
