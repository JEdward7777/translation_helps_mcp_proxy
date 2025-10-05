# MCP Proxy Server for Translation Helps

A Python **stdio MCP server** that bridges MCP clients with the translation-helps-mcp server. This proxy handles JSON-RPC 2.0 formatting and protocol translation to make the upstream HTTP server fully compatible with MCP clients.

## 🎯 Current Status

**✅ PRODUCTION READY** - All functionality working as of October 2025

- **MCP Initialization**: ✅ Proper JSON-RPC 2.0 handshake
- **Tool Discovery**: ✅ Discovers all 12 tools from upstream server
- **Tool Execution**: ✅ Successfully executes all tools including fetch_scripture
- **Stdio Protocol**: ✅ Complete MCP stdio workflow operational
- **Error Handling**: ✅ Graceful error handling and cleanup

**Test Results**: **4/4 comprehensive tests passing** (100% operational)

## 🔧 Technical Architecture

### Protocol Flow
```
MCP Client ←→ Proxy Server ←→ Upstream Server
(stdio)        (stdio)         (HTTP)
JSON-RPC 2.0   JSON-RPC 2.0    API endpoints
```

### Key Features
- **Protocol Translation**: Converts between MCP stdio and HTTP API calls
- **Response Formatting**: Handles various upstream response formats (MCP content, scripture data, wrapped results)
- **Smart Routing**: Routes `fetch_scripture` calls to dedicated `/api/fetch-scripture` endpoint
- **Error Recovery**: Robust async error handling and resource cleanup

## 📁 Project Structure

```
mcp-proxy/
├── mcp_proxy_server.py         # Main proxy server
├── test_mcp_proxy.py          # Comprehensive test suite (4/4 passing)
├── requirements.txt           # Python dependencies 
├── setup.sh / setup.bat       # Cross-platform setup scripts
├── README.md                  # This file
├── CORRECT_mcp_config.json    # Example MCP client configuration
└── venv/                      # Virtual environment (created by setup)
```

## ⚡ Quick Start

### Automated Setup
```bash
cd mcp-proxy

# Linux/macOS
./setup.sh

# Windows  
setup.bat
```

### Manual Setup
```bash
# Create and activate virtual environment
python3 -m venv venv

# Activate virtual environment (REQUIRED for all operations)
. venv/bin/activate  # Linux/macOS (note: use dot, not 'source')
# OR: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Test the server
python test_mcp_proxy.py

# Run the server
python mcp_proxy_server.py
```

**Important**: Always activate the virtual environment before running any commands. Use `. venv/bin/activate` (with dot) if `source` command is not available.

## 🧪 Testing

### Comprehensive Test Suite
Run all tests:
```bash
# Option 1: Direct path to venv Python
./venv/bin/python test_mcp_proxy.py

# Option 2: Activate venv first (recommended)
. venv/bin/activate  # Use dot if 'source' doesn't work
python test_mcp_proxy.py
```

**Test Coverage**:
1. **Upstream Connectivity** ✅ - Verifies connection and tool discovery
2. **MCP Protocol** ✅ - Tests JSON-RPC 2.0 initialization  
3. **Tool Execution** ✅ - Validates tool calls including fetch_scripture
4. **Stdio MCP Workflow** ✅ - Complete end-to-end John 3:16 test

**Expected Output**:
```
🧪 MCP Proxy Server - Comprehensive Test Suite
============================================================
✅ PASS | Upstream Connectivity
✅ PASS | MCP Protocol  
✅ PASS | Tool Execution
✅ PASS | Stdio MCP Workflow

Results: 4/4 tests passed
🎉 ALL TESTS PASSED! MCP Proxy Server is fully functional.
```

## 🚀 Usage

### Basic Usage
```bash
# IMPORTANT: Always activate venv first
. venv/bin/activate  # Use dot if 'source' doesn't work

# Default: connects to https://translation-helps-mcp.pages.dev/api/mcp
python mcp_proxy_server.py
```

### Advanced Options
```bash
# IMPORTANT: Ensure venv is activated first
. venv/bin/activate

# Different upstream URL
python mcp_proxy_server.py --upstream-url "http://localhost:5173/api/mcp"

# Debug mode (detailed logging)
python mcp_proxy_server.py --debug

# Combined
python mcp_proxy_server.py --upstream-url "http://localhost:5173/api/mcp" --debug
```

### MCP Client Configuration

**stdio MCP Server Configuration**:
```json
{
  "translation-helps-mcp-proxy": {
    "command": "python",
    "args": ["mcp_proxy_server.py"],
    "cwd": "/absolute/path/to/mcp-proxy"
  }
}
```

**Important**: Use absolute paths in `cwd` for MCP client compatibility.

## 🛠️ Available Tools (12 Total)

The proxy automatically discovers and forwards all tools from the upstream server:

| Tool | Description | Status |
|------|-------------|--------|
| `get_system_prompt` | Get system prompt and constraints | ✅ Working |
| `fetch_scripture` | Fetch Bible scripture text | ✅ Working |
| `fetch_translation_notes` | Get translation notes for references | ✅ Working |
| `fetch_translation_questions` | Get translation questions | ✅ Working |
| `browse_translation_words` | Browse translation vocabulary | ✅ Working |
| `get_context` | Get contextual information | ✅ Working |
| `extract_references` | Parse Bible references from text | ✅ Working |
| `fetch_resources` | Get multiple resource types | ✅ Working |
| `get_words_for_reference` | Get words for specific references | ✅ Working |
| `get_translation_word` | Get specific translation words | ✅ Working |
| `search_resources` | Search across resource types | ✅ Working |
| `get_languages` | Get available languages | ✅ Working |

### Example: Fetching John 3:16
The `fetch_scripture` tool successfully retrieves Bible verses with multiple translations:

```json
{
  "name": "fetch_scripture",
  "arguments": {"reference": "John 3:16"}
}
```

Returns: "For God so loved the world, that he gave his One and Only Son, so that everyone believing in him would not perish but would have eternal life." (ULT v86) plus UST, T4T, and UEB translations.

## 🔍 Response Format Handling

The proxy intelligently handles various upstream response formats:

1. **Scripture Format**: `{"scripture": [...]}` → Formatted multi-translation display
2. **MCP Format**: `{"content": [...]}` → Proper MCP TextContent objects
3. **Wrapped Results**: `{"result": ...}` → Extracts and formats result
4. **Raw JSON**: Any other format → JSON stringification fallback

## 🐛 Troubleshooting

### Import Errors
```bash
# Ensure virtual environment is activated (MOST COMMON ISSUE)
. venv/bin/activate  # Use dot if 'source' command doesn't work

# Reinstall dependencies
pip install -r requirements.txt
```

**⚠️ Common Issue**: Most problems are caused by forgetting to activate the virtual environment. Always run `. venv/bin/activate` before any Python commands.

### Connection Issues
```bash
# IMPORTANT: Activate venv first
. venv/bin/activate

# Test upstream connectivity
python -c "
import asyncio, httpx
async def test():
    client = httpx.AsyncClient(verify=False)
    r = await client.get('https://translation-helps-mcp.pages.dev/api/mcp?method=ping')
    print(f'Status: {r.status_code}, Response: {r.text[:100]}')
    await client.aclose()
asyncio.run(test())
"
```

### Debug Mode
```bash
# IMPORTANT: Activate venv first
. venv/bin/activate

python mcp_proxy_server.py --debug
```
Shows detailed upstream communication, response parsing, and error details.

### Virtual Environment Notes
- **Always activate venv**: All Python commands require the virtual environment to be activated
- **Use dot syntax**: If `source venv/bin/activate` doesn't work, use `. venv/bin/activate`
- **Per-session**: You need to activate the venv in each new terminal session
- **Verification**: Your prompt should show `(venv)` when the virtual environment is active

## 📊 Performance & Reliability

- **Timeout**: 30-second timeout for upstream requests
- **Connection**: Persistent HTTP client with connection pooling
- **Memory**: Minimal memory footprint, suitable for long-running processes
- **SSL**: Handles certificate issues by disabling verification for upstream server
- **Async**: Proper async/await with TaskGroup error handling

## 🔮 Technical Details

### Key Dependencies
```python
mcp>=1.0.0                 # Official MCP SDK
httpx>=0.25.0             # Async HTTP client  
typing-extensions>=4.0.0   # Type hints support
```

### Core Architecture
- **`MCPProxyServer`**: Main proxy class handling MCP protocol and upstream communication
- **Smart Tool Routing**: Special handling for `fetch_scripture` and other tools
- **Response Transformation**: Converts various upstream formats to proper MCP responses
- **Error Handling**: Graceful async error handling with proper cleanup

### Future Enhancements
Potential improvements for advanced use cases:
- [ ] Convert to pytest-based test suite for better CI/CD integration
- [ ] Add response caching for frequently called tools
- [ ] Support for additional MCP features (resources, prompts)
- [ ] Metrics and monitoring capabilities
- [ ] Rate limiting and request queuing

## 📝 License

This proxy server is provided as-is to enable compatibility with the translation-helps-mcp service.

---

**🎉 Production Ready** - The proxy server successfully bridges MCP clients with the upstream translation-helps-mcp server, with all tools working including Bible verse fetching via `fetch_scripture`.