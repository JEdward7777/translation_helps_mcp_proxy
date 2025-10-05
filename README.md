# MCP Proxy Server for Translation Helps

A Python **stdio MCP server** that fixes JSON-RPC 2.0 formatting issues for the translation-helps-mcp server. This acts as middleware to make the existing HTTP server compatible with MCP clients.

## Protocol Types & Communication Flow

```
MCP Client ←→ Proxy Server ←→ Upstream Server
(stdio)        (stdio)         (HTTP)
JSON-RPC 2.0   JSON-RPC 2.0    Non-standard JSON
```

**Your Original Server**: `streamable-http` MCP (broken)
- URL: `https://translation-helps-mcp.pages.dev/api/mcp`
- Protocol: HTTP with non-standard JSON responses
- Missing: `jsonrpc: "2.0"`, `id` fields, proper `result` wrapping

**This Proxy Server**: `stdio` MCP (the fix)
- Protocol: Standard Input/Output with proper JSON-RPC 2.0
- Acts as bridge between MCP clients and your HTTP server

## Problem Solved

The proxy translates between proper MCP protocol and the upstream server's non-standard format, enabling any MCP client to connect successfully.

## Setup

### 1. Create Virtual Environment

```bash
cd mcp-proxy
python3 -m venv venv
```

### 2. Activate Virtual Environment

**On Linux/macOS:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the proxy server with default settings:

```bash
python mcp_proxy_server.py
```

This will:
- Connect to `https://translation-helps-mcp.pages.dev/api/mcp` as the upstream server
- Start an MCP server that properly formats responses
- Log activity at INFO level

### Advanced Usage

```bash
# Use a different upstream URL
python mcp_proxy_server.py --upstream-url "http://localhost:5173/api/mcp"

# Enable debug logging
python mcp_proxy_server.py --debug

# Combine options
python mcp_proxy_server.py --upstream-url "http://localhost:5173/api/mcp" --debug
```

### Command Line Options

- `--upstream-url`: URL of the upstream MCP server to proxy (default: https://translation-helps-mcp.pages.dev/api/mcp)
- `--debug`: Enable debug logging to see detailed request/response information

## Connecting to the Proxy

Once the proxy is running, you can connect your MCP client to it instead of the original server. The proxy will handle all the protocol translation automatically.

### MCP Configuration

If you're using this with an MCP client, configure it to connect to the proxy server instead of the original URL. The proxy runs as a standard MCP server over stdio.

Example configuration:
```json
{
  "translation-helps-mcp-proxy": {
    "command": "python",
    "args": ["/path/to/mcp-proxy/mcp_proxy_server.py"],
    "cwd": "/path/to/mcp-proxy"
  }
}
```

## Features

### Supported Tools

The proxy automatically discovers and forwards all tools from the upstream server, including:

- `fetch_scripture` - Fetch Bible scripture text
- `fetch_translation_notes` - Get translation notes for references
- `fetch_translation_questions` - Get translation questions
- `browse_translation_words` - Browse translation vocabulary
- `get_context` - Get contextual information
- `extract_references` - Parse Bible references from text
- `fetch_resources` - Get multiple resource types
- `get_words_for_reference` - Get words for specific references
- `get_translation_word` - Get specific translation words
- `search_resources` - Search across resource types
- `get_languages` - Get available languages
- `get_system_prompt` - Get system prompt information

### Response Format Translation

The proxy handles various response formats from the upstream server:

1. **MCP-like format**: When upstream returns `{"content": [...]}`, it properly formats as MCP TextContent
2. **Wrapped results**: When upstream returns `{"result": ...}`, it extracts and formats the result
3. **Raw responses**: Falls back to JSON stringification for any other format

### Error Handling

- Timeouts: 30-second timeout for upstream requests
- Connection errors: Graceful handling with informative error messages
- Invalid JSON: Proper error reporting when upstream returns malformed responses
- Tool errors: Individual tool failures don't crash the server

## Development

### Testing the Connection

You can test if the upstream server is reachable:

```bash
python -c "
import asyncio
import httpx

async def test():
    client = httpx.AsyncClient()
    response = await client.get('https://translation-helps-mcp.pages.dev/api/mcp?method=ping')
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text}')
    await client.aclose()

asyncio.run(test())
"
```

### Debug Mode

Run with `--debug` to see detailed request/response logs:

```bash
python mcp_proxy_server.py --debug
```

This will show:
- Upstream request details
- Response parsing steps
- Tool call forwarding
- Error details

## Troubleshooting

### Import Errors

If you see import errors for `mcp` or `httpx`:

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Connection Errors

If the proxy can't connect to the upstream server:

1. Check the upstream URL is correct
2. Test the connection manually (see Testing section above)
3. Check firewall/network settings
4. Try with `--debug` to see detailed error messages

### Tool Errors

If specific tools fail:

1. Run with `--debug` to see the upstream response
2. Check if the tool exists in the upstream server
3. Verify the tool arguments are correct

## Architecture

```
MCP Client → MCP Proxy Server → Upstream Server (translation-helps-mcp)
             (Proper JSON-RPC)   (Non-standard format)
```

The proxy:
1. Receives standard MCP requests
2. Translates them to the upstream server's expected format
3. Calls the upstream server
4. Translates responses back to proper MCP format
5. Returns properly formatted JSON-RPC 2.0 responses

## License

This proxy server is provided as-is to enable compatibility with the translation-helps-mcp service.