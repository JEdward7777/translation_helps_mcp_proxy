"""Shared test fixtures for MCP Proxy Server test suite."""

import pytest
import pytest_asyncio
from pathlib import Path
import sys

# Add src directory to path so we can import from the package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from translation_helps_mcp_proxy.mcp_proxy_server import MCPProxyServer


@pytest_asyncio.fixture
async def proxy_server():
    """Create a test MCPProxyServer instance."""
    proxy = MCPProxyServer(verify_ssl=False)
    try:
        yield proxy
    finally:
        # Ensure cleanup
        if not proxy.client.is_closed:
            await proxy.client.aclose()


@pytest.fixture
def test_server_command():
    """Command to start the MCP server for subprocess tests."""
    package_dir = Path(__file__).parent.parent / "src" / "translation_helps_mcp_proxy"
    return [sys.executable, str(package_dir / "mcp_proxy_server.py")]


@pytest.fixture
def mcp_initialize_request():
    """Standard MCP initialize request for testing."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {"listChanged": True},
                "sampling": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }


@pytest.fixture
def mcp_initialized_notification():
    """Standard MCP initialized notification for testing."""
    return {
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
        "params": {}
    }


@pytest.fixture
def john_3_16_tool_request():
    """Standard John 3:16 fetch_scripture request for testing."""
    return {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "fetch_scripture",
            "arguments": {
                "reference": "John 3:16"
            }
        }
    }