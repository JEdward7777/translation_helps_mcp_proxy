#!/usr/bin/env python3
"""
MCP Proxy Server - Translation Helps

A proxy server that fixes JSON-RPC 2.0 formatting issues for the translation-helps-mcp server.
This acts as a middleware to make the existing server compatible with MCP clients.
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, Optional
import httpx
from mcp.server import Server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    GetPromptRequest,
    GetPromptResult,
    InitializeRequest,
    InitializeResult,
    ListPromptsRequest,
    ListPromptsResult,
    ListResourcesRequest,
    ListResourcesResult,
    ListToolsRequest,
    ListToolsResult,
    Prompt,
    Resource,
    TextContent,
    Tool,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPProxyServer:
    """Proxy server that translates between proper MCP and the broken upstream server."""
    
    def __init__(self, upstream_url: str = "https://translation-helps-mcp.pages.dev/api/mcp", verify_ssl: bool = False):
        self.upstream_url = upstream_url
        self.server = Server("translation-helps-mcp-proxy")
        self.client = httpx.AsyncClient(timeout=30.0, verify=verify_ssl)
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all the MCP method handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools from the upstream server."""
            try:
                # Call upstream server's tools/list method
                response = await self._call_upstream("tools/list", {})
                
                if not response or "tools" not in response:
                    logger.warning("No tools found in upstream response")
                    return []
                
                # Convert upstream tool format to proper MCP Tool objects
                tools = []
                for tool_data in response["tools"]:
                    try:
                        tool = Tool(
                            name=tool_data["name"],
                            description=tool_data["description"],
                            inputSchema=tool_data.get("inputSchema", {})
                        )
                        tools.append(tool)
                    except Exception as e:
                        logger.error(f"Error parsing tool {tool_data.get('name', 'unknown')}: {e}")
                        continue
                
                logger.info(f"Successfully loaded {len(tools)} tools from upstream")
                return tools
                
            except Exception as e:
                logger.error(f"Error listing tools: {e}")
                return []
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Call a tool on the upstream server."""
            try:
                logger.info(f"Calling tool: {name} with args: {arguments}")
                
                # Call upstream server's tools/call method
                response = await self._call_upstream("tools/call", {
                    "name": name,
                    "arguments": arguments
                })
                
                if not response:
                    return [TextContent(type="text", text="Error: No response from upstream server")]
                
                # Handle different response formats from upstream
                if "content" in response:
                    # Upstream returns MCP-like format
                    content_list = []
                    for item in response["content"]:
                        if item.get("type") == "text":
                            content_list.append(TextContent(type="text", text=item["text"]))
                    return content_list if content_list else [TextContent(type="text", text="Empty response")]
                
                elif "result" in response:
                    # Upstream returns wrapped result
                    result_text = json.dumps(response["result"], indent=2) if isinstance(response["result"], dict) else str(response["result"])
                    return [TextContent(type="text", text=result_text)]
                
                else:
                    # Fallback: stringify the whole response
                    result_text = json.dumps(response, indent=2)
                    return [TextContent(type="text", text=result_text)]
                    
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return [TextContent(type="text", text=f"Error calling tool {name}: {str(e)}")]
    
    async def _call_upstream(self, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call the upstream server and handle response format issues."""
        try:
            # Prepare request body - the upstream server expects non-standard format
            if method == "tools/list":
                # For tools/list, use GET method as the server supports it
                response = await self.client.get(f"{self.upstream_url}?method=tools/list")
            else:
                # For other methods, use POST
                request_body = {
                    "method": method,
                    "params": params
                }
                
                response = await self.client.post(
                    self.upstream_url,
                    json=request_body,
                    headers={"Content-Type": "application/json"}
                )
            
            if response.status_code != 200:
                logger.error(f"Upstream server returned status {response.status_code}: {response.text}")
                return None
            
            try:
                data = response.json()
                logger.debug(f"Upstream response for {method}: {json.dumps(data, indent=2)[:500]}...")
                return data
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from upstream server: {e}")
                logger.error(f"Response text: {response.text[:500]}...")
                return None
                
        except httpx.TimeoutException:
            logger.error(f"Timeout calling upstream server for method {method}")
            return None
        except Exception as e:
            logger.error(f"Error calling upstream server for method {method}: {e}")
            return None
    
    async def run(self):
        """Run the proxy server."""
        try:
            # Test connection to upstream server first
            logger.info(f"Testing connection to upstream server: {self.upstream_url}")
            test_response = await self.client.get(f"{self.upstream_url}?method=ping")
            if test_response.status_code == 200:
                logger.info("Successfully connected to upstream server")
            else:
                logger.warning(f"Upstream server test returned status {test_response.status_code}")
            
            # Run the MCP server
            logger.info("Starting MCP proxy server...")
            async with self.server.create_session() as session:
                await session.run()
                
        except KeyboardInterrupt:
            logger.info("Shutting down proxy server...")
        except Exception as e:
            logger.error(f"Error running proxy server: {e}")
            raise
        finally:
            await self.client.aclose()

async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Proxy Server for Translation Helps")
    parser.add_argument(
        "--upstream-url",
        default="https://translation-helps-mcp.pages.dev/api/mcp",
        help="URL of the upstream MCP server to proxy"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and run the proxy server
    proxy = MCPProxyServer(upstream_url=args.upstream_url)
    await proxy.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)