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
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPProxyServer:
    """Proxy server that translates between proper MCP and the broken upstream server."""
    
    def __init__(self, upstream_url: str = "https://translation-helps-mcp.pages.dev/api/mcp",
                 verify_ssl: bool = False, enabled_tools: Optional[list[str]] = None):
        self.upstream_url = upstream_url
        self.enabled_tools = enabled_tools  # None means all tools enabled
        self._upstream_tools = None  # Cache for upstream tools
        
        # Initialize server with proper name
        self.server = Server("translation-helps-mcp-proxy")
        self.client = httpx.AsyncClient(timeout=30.0, verify=verify_ssl)
        
        # Set up server info and capabilities
        self.server.server_info = {
            "name": "translation-helps-mcp-proxy",
            "version": "1.0.0"
        }
        
        # Register handlers
        self._register_handlers()
    
    async def _validate_enabled_tools(self, upstream_tools: list[dict]):
        """Validate that all enabled tools exist in upstream server."""
        if self.enabled_tools is None:
            return
            
        upstream_tool_names = {tool['name'] for tool in upstream_tools}
        
        # Check for unknown tools
        unknown_tools = set(self.enabled_tools) - upstream_tool_names
        if unknown_tools:
            raise ValueError(f"Unknown tools specified: {', '.join(unknown_tools)}")
    
    async def _get_filtered_tools(self) -> list[Tool]:
        """Get filtered list of tools based on enabled_tools."""
        # Get all upstream tools
        upstream_response = await self._call_upstream('tools/list', {})
        if not upstream_response or 'tools' not in upstream_response:
            return []
            
        upstream_tools = upstream_response['tools']
        
        # Validate enabled tools on first call
        await self._validate_enabled_tools(upstream_tools)
            
        # Convert to Tool objects and filter
        tools = []
        for tool_data in upstream_tools:
            # Skip if tool filtering is enabled and this tool is not in the list
            if self.enabled_tools is not None and tool_data['name'] not in self.enabled_tools:
                continue
                
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
                
        return tools
    
    async def _is_tool_enabled(self, tool_name: str) -> bool:
        """Check if a specific tool is enabled."""
        if self.enabled_tools is None:
            return True  # All tools enabled by default
        return tool_name in self.enabled_tools
    
    def _register_handlers(self):
        """Register all the MCP method handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools from the upstream server, filtered by enabled_tools."""
            try:
                # Use filtered tools instead of all upstream tools
                tools = await self._get_filtered_tools()
                
                logger.info(f"Successfully loaded {len(tools)} tools from upstream")
                if self.enabled_tools is not None:
                    logger.info(f"Tool filtering active: {len(tools)} of total tools enabled")
                    logger.info(f"Enabled tools: {[tool.name for tool in tools]}")
                
                return tools
                
            except asyncio.CancelledError:
                logger.info("list_tools cancelled")
                raise
            except Exception as e:
                logger.error(f"Error listing tools: {e}")
                import traceback
                logger.error(f"list_tools traceback: {traceback.format_exc()}")
                return []
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Call a tool on the upstream server."""
            try:
                logger.info(f"Calling tool: {name} with args: {arguments}")
                
                # Check if tool is enabled
                if not await self._is_tool_enabled(name):
                    logger.warning(f"Tool {name} is disabled by configuration")
                    return [TextContent(type="text", text=f"Tool '{name}' is disabled. Enable it with --enabled-tools option.")]
                
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
                
                elif "scripture" in response:
                    # Direct API endpoint returns scripture format
                    scripture_list = response["scripture"]
                    if scripture_list:
                        # Format the scripture nicely for display
                        formatted_text = ""
                        for i, scripture in enumerate(scripture_list):
                            text = scripture.get("text", "")
                            translation = scripture.get("translation", "")
                            if i > 0:
                                formatted_text += "\n\n"
                            formatted_text += f"{text}"
                            if translation:
                                formatted_text += f" ({translation})"
                        
                        return [TextContent(type="text", text=formatted_text)]
                    else:
                        return [TextContent(type="text", text="No scripture text found")]
                
                elif "notes" in response or "verseNotes" in response or "items" in response:
                    # Translation notes endpoint format
                    notes = response.get("notes") or response.get("verseNotes") or response.get("items", [])
                    if notes:
                        formatted_text = f"Translation Notes for {arguments.get('reference', 'Reference')}:\n\n"
                        for i, note in enumerate(notes):
                            note_content = note.get("Note") or note.get("note") or note.get("text") or note.get("content") or str(note)
                            formatted_text += f"{i + 1}. {note_content}\n\n"
                        return [TextContent(type="text", text=formatted_text)]
                    else:
                        return [TextContent(type="text", text="No translation notes found for this reference.")]
                
                elif "words" in response:
                    # Translation words endpoint format
                    words = response["words"]
                    if words:
                        formatted_text = f"Translation Words for {arguments.get('reference', 'Reference')}:\n\n"
                        for word in words:
                            term = word.get("term") or word.get("name") or "Unknown Term"
                            definition = word.get("definition") or word.get("content") or "No definition available"
                            formatted_text += f"**{term}**\n{definition}\n\n"
                        return [TextContent(type="text", text=formatted_text)]
                    else:
                        return [TextContent(type="text", text="No translation words found for this reference.")]
                
                elif "term" in response and "definition" in response:
                    # Single translation word format
                    term = response["term"]
                    definition = response["definition"]
                    formatted_text = f"**{term}**\n{definition}"
                    return [TextContent(type="text", text=formatted_text)]
                
                elif "questions" in response:
                    # Translation questions endpoint format
                    questions = response["questions"]
                    if questions:
                        formatted_text = f"Translation Questions for {arguments.get('reference', 'Reference')}:\n\n"
                        for i, q in enumerate(questions):
                            question = q.get("question") or q.get("Question") or "No question"
                            answer = q.get("answer") or q.get("Answer") or "No answer"
                            formatted_text += f"Q{i + 1}: {question}\nA: {answer}\n\n"
                        return [TextContent(type="text", text=formatted_text)]
                    else:
                        return [TextContent(type="text", text="No translation questions found for this reference.")]
                
                elif "result" in response:
                    # Upstream returns wrapped result
                    result_text = json.dumps(response["result"], indent=2) if isinstance(response["result"], dict) else str(response["result"])
                    return [TextContent(type="text", text=result_text)]
                
                else:
                    # Fallback: stringify the whole response
                    result_text = json.dumps(response, indent=2)
                    return [TextContent(type="text", text=result_text)]
                    
            except asyncio.CancelledError:
                logger.info(f"call_tool {name} cancelled")
                raise
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                import traceback
                logger.error(f"call_tool {name} traceback: {traceback.format_exc()}")
                return [TextContent(type="text", text=f"Error calling tool {name}: {str(e)}")]
    
    async def _call_upstream(self, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call the upstream server and handle response format issues."""
        try:
            # Prepare request body - the upstream server expects non-standard format
            if method == "tools/list":
                # For tools/list, use GET method as the server supports it
                response = await self.client.get(f"{self.upstream_url}?method=tools/list")
            elif method == "tools/call":
                # Tool calls need to go to specific endpoints, not the MCP endpoint
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                
                # Route to the specific tool endpoint
                base_url = self.upstream_url.replace("/api/mcp", "")
                
                if tool_name == "fetch_scripture":
                    # Use the direct API endpoint for fetch_scripture
                    api_url = f"{base_url}/api/fetch-scripture"
                    
                    # Convert arguments to query parameters
                    query_params = {}
                    if "reference" in tool_args:
                        query_params["reference"] = tool_args["reference"]
                    if "language" in tool_args:
                        query_params["language"] = tool_args["language"]
                    if "organization" in tool_args:
                        query_params["organization"] = tool_args["organization"]
                    
                    response = await self.client.get(api_url, params=query_params)
                    
                elif tool_name == "fetch_translation_notes":
                    # Route to translation-notes endpoint
                    api_url = f"{base_url}/api/translation-notes"
                    
                    query_params = {}
                    if "reference" in tool_args:
                        query_params["reference"] = tool_args["reference"]
                    if "language" in tool_args:
                        query_params["language"] = tool_args["language"]
                    if "organization" in tool_args:
                        query_params["organization"] = tool_args["organization"]
                    
                    response = await self.client.get(api_url, params=query_params)
                    
                elif tool_name == "fetch_translation_questions":
                    # Route to translation-questions endpoint
                    api_url = f"{base_url}/api/translation-questions"
                    
                    query_params = {}
                    if "reference" in tool_args:
                        query_params["reference"] = tool_args["reference"]
                    if "language" in tool_args:
                        query_params["language"] = tool_args["language"]
                    if "organization" in tool_args:
                        query_params["organization"] = tool_args["organization"]
                    
                    response = await self.client.get(api_url, params=query_params)
                    
                elif tool_name == "get_translation_word" or tool_name == "fetch_translation_words":
                    # Route to fetch-translation-words endpoint
                    api_url = f"{base_url}/api/fetch-translation-words"
                    
                    query_params = {}
                    # Handle both 'reference' and 'wordId' parameters
                    if "reference" in tool_args:
                        query_params["reference"] = tool_args["reference"]
                    if "wordId" in tool_args:
                        query_params["wordId"] = tool_args["wordId"]
                    if "language" in tool_args:
                        query_params["language"] = tool_args["language"]
                    if "organization" in tool_args:
                        query_params["organization"] = tool_args["organization"]
                    
                    response = await self.client.get(api_url, params=query_params)
                    
                elif tool_name == "browse_translation_words":
                    # Route to browse-translation-words endpoint
                    api_url = f"{base_url}/api/browse-translation-words"
                    
                    query_params = {}
                    if "language" in tool_args:
                        query_params["language"] = tool_args["language"]
                    if "organization" in tool_args:
                        query_params["organization"] = tool_args["organization"]
                    if "category" in tool_args:
                        query_params["category"] = tool_args["category"]
                    if "search" in tool_args:
                        query_params["search"] = tool_args["search"]
                    if "limit" in tool_args:
                        query_params["limit"] = tool_args["limit"]
                    
                    response = await self.client.get(api_url, params=query_params)
                    
                elif tool_name == "get_context":
                    # Route to get-context endpoint
                    api_url = f"{base_url}/api/get-context"
                    
                    query_params = {}
                    if "reference" in tool_args:
                        query_params["reference"] = tool_args["reference"]
                    if "language" in tool_args:
                        query_params["language"] = tool_args["language"]
                    if "organization" in tool_args:
                        query_params["organization"] = tool_args["organization"]
                    
                    response = await self.client.get(api_url, params=query_params)
                    
                elif tool_name == "extract_references":
                    # Route to extract-references endpoint
                    api_url = f"{base_url}/api/extract-references"
                    
                    query_params = {}
                    if "text" in tool_args:
                        query_params["text"] = tool_args["text"]
                    if "includeContext" in tool_args:
                        query_params["includeContext"] = tool_args["includeContext"]
                    
                    response = await self.client.get(api_url, params=query_params)
                    
                else:
                    # For other tools, try the MCP endpoint first (fallback)
                    request_body = {
                        "method": method,
                        "params": params
                    }
                    
                    response = await self.client.post(
                        self.upstream_url,
                        json=request_body,
                        headers={"Content-Type": "application/json"}
                    )
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
    
    async def test_connection(self):
        """Test connection to upstream server."""
        try:
            logger.info(f"Testing connection to upstream server: {self.upstream_url}")
            test_response = await self.client.get(f"{self.upstream_url}?method=ping")
            if test_response.status_code == 200:
                logger.info("Successfully connected to upstream server")
                return True
            else:
                logger.warning(f"Upstream server test returned status {test_response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to upstream server: {e}")
            return False

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
    parser.add_argument(
        "--enabled-tools",
        type=str,
        help="Comma-separated list of tools to enable (default: all tools enabled)"
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List all available tools from upstream server and exit"
    )
    
    args = parser.parse_args()
    
    # Handle --list-tools option
    if args.list_tools:
        print("📋 Discovering available tools from upstream server...")
        temp_proxy = MCPProxyServer(upstream_url=args.upstream_url, verify_ssl=False)
        try:
            upstream_response = await temp_proxy._call_upstream('tools/list', {})
            if upstream_response and 'tools' in upstream_response:
                tools = upstream_response['tools']
                print(f"\n✅ Found {len(tools)} available tools:\n")
                for i, tool in enumerate(tools, 1):
                    print(f"{i:2d}. {tool['name']:<25} - {tool['description']}")
                print(f"\n💡 Usage: --enabled-tools \"tool1,tool2,tool3\"")
                print(f"   Example: --enabled-tools \"fetch_scripture,fetch_translation_notes\"")
            else:
                print("❌ Unable to discover tools from upstream server")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Error discovering tools: {e}")
            sys.exit(1)
        finally:
            if not temp_proxy.client.is_closed:
                await temp_proxy.client.aclose()
        sys.exit(0)
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Parse enabled tools
    enabled_tools = None
    if args.enabled_tools:
        enabled_tools = [tool.strip() for tool in args.enabled_tools.split(',')]
        logger.info(f"Tool filtering enabled: {enabled_tools}")
    
    # Create the proxy server
    proxy = MCPProxyServer(upstream_url=args.upstream_url, enabled_tools=enabled_tools)
    
    try:
        # Test connection
        await proxy.test_connection()
        
        # Create initialization options
        init_options = InitializationOptions(
            server_name="translation-helps-mcp-proxy",  # Match the name passed to Server()
            server_version="1.0.0",  # Set server version
            capabilities=proxy.server.get_capabilities(
                notification_options=NotificationOptions(),  # Use defaults
                experimental_capabilities={},  # No experimental capabilities needed
            ),
        )
        
        # Run the MCP server using stdio
        logger.info("Starting MCP proxy server...")
        async with stdio_server() as (read_stream, write_stream):
            await proxy.server.run(read_stream, write_stream, init_options)
            
    except asyncio.CancelledError:
        logger.info("Server cancelled, shutting down gracefully")
        raise
    except Exception as e:
        logger.error(f"Error running MCP server: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
    finally:
        try:
            if not proxy.client.is_closed:
                await proxy.client.aclose()
        except Exception as e:
            logger.warning(f"Error closing HTTP client: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)