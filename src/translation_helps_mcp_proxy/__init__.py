"""Translation Helps MCP Proxy Package

A Python package that provides MCP (Model Context Protocol) proxy functionality
for the translation-helps-mcp server, with optional MCPO REST API integration.
"""

__version__ = "1.0.0"
__author__ = "Translation Helps MCP Team"

from .mcp_proxy_server import MCPProxyServer

__all__ = ["MCPProxyServer"]