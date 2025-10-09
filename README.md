# MCP Proxy Server for Translation Helps

A Python **stdio MCP server** that bridges MCP clients with the translation-helps-mcp server. This proxy handles JSON-RPC 2.0 formatting and protocol translation to make the upstream HTTP server fully compatible with MCP clients.

## 🎯 Current Status

**✅ PRODUCTION READY** - All functionality working as of October 2025

- **MCP Initialization**: ✅ Proper JSON-RPC 2.0 handshake
- **Tool Discovery**: ✅ Discovers all 12 tools from upstream server
- **Tool Execution**: ✅ Successfully executes all tools including fetch_scripture
- **Stdio Protocol**: ✅ Complete MCP stdio workflow operational
- **Error Handling**: ✅ Graceful error handling and cleanup

**Test Results**: **16/16 comprehensive tests passing** (100% operational)

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
├── test_mcp_proxy.py          # Legacy test suite (kept for reference)
├── tests/                     # Modern pytest test suite
│   ├── __init__.py           # Package initialization
│   ├── conftest.py           # Shared test fixtures
│   ├── test_upstream_connectivity.py  # Upstream connection tests
│   ├── test_mcp_protocol.py          # MCP protocol tests
│   ├── test_tool_execution.py        # Tool execution tests
│   ├── test_stdio_workflow.py        # End-to-end workflow tests
│   ├── test_fetch_translation_notes.py # Translation notes tool tests
│   └── test_get_translation_word.py    # Translation word tool tests
├── pytest.ini               # Pytest configuration
├── requirements.txt          # Python dependencies (includes pytest)
├── setup.sh / setup.bat      # Cross-platform setup scripts
├── README.md                 # This file
├── CORRECT_mcp_config.json   # Example MCP client configuration
└── venv/                     # Virtual environment (created by setup)
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

# Test the server (pytest - recommended)
pytest

# Or legacy test (still available)
python test_mcp_proxy.py

# Run the server
python mcp_proxy_server.py
```

**Important**: Always activate the virtual environment before running any commands. Use `. venv/bin/activate` (with dot) if `source` command is not available.

## 🧪 Testing

### Modern pytest Test Suite (Recommended)
Run all tests:
```bash
# Activate venv first (REQUIRED)
. venv/bin/activate  # Use dot if 'source' doesn't work

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test files
pytest tests/test_upstream_connectivity.py
pytest tests/test_tool_execution.py
pytest tests/test_fetch_translation_notes.py
pytest tests/test_get_translation_word.py

# Run specific test functions
pytest tests/test_stdio_workflow.py::test_stdio_workflow
pytest tests/test_fetch_translation_notes.py::test_fetch_translation_notes_basic
pytest tests/test_get_translation_word.py::test_get_translation_word_basic

# Run tests in parallel (faster)
pytest -n auto
```

### Legacy Test Suite (Available for Reference)
```bash
# Original comprehensive test (still works)
. venv/bin/activate
python test_mcp_proxy.py
```

**Test Coverage** (Both Suites):
1. **Upstream Connectivity** ✅ - Verifies connection and tool discovery
2. **MCP Protocol** ✅ - Tests JSON-RPC 2.0 initialization
3. **Tool Execution** ✅ - Validates tool calls including fetch_scripture
4. **Stdio MCP Workflow** ✅ - Complete end-to-end John 3:16 test
5. **Translation Notes** ✅ - Tests fetch_translation_notes tool (7 test cases)
6. **Translation Words** ✅ - Tests get_translation_word tool (9 test cases)

**pytest Expected Output**:
```
========================= test session starts =========================
collected 16 items

tests/test_upstream_connectivity.py::test_upstream_connectivity PASSED
tests/test_upstream_connectivity.py::test_tools_list_format PASSED
tests/test_mcp_protocol.py::test_mcp_protocol_initialization PASSED
tests/test_mcp_protocol.py::test_mcp_response_format PASSED
tests/test_tool_execution.py::test_tool_execution PASSED
tests/test_tool_execution.py::test_get_system_prompt_tool PASSED
tests/test_tool_execution.py::test_fetch_scripture_tool PASSED
tests/test_stdio_workflow.py::test_stdio_workflow PASSED
tests/test_fetch_translation_notes.py::test_fetch_translation_notes_basic PASSED
tests/test_fetch_translation_notes.py::test_fetch_translation_notes_missing_reference PASSED
tests/test_fetch_translation_notes.py::test_fetch_translation_notes_different_book PASSED
tests/test_fetch_translation_notes.py::test_fetch_translation_notes_default_params PASSED
tests/test_fetch_translation_notes.py::test_fetch_translation_notes_invalid_reference PASSED
tests/test_fetch_translation_notes.py::test_fetch_translation_notes_response_structure PASSED
tests/test_fetch_translation_notes.py::test_fetch_translation_notes_tool_integration PASSED
tests/test_get_translation_word.py::test_get_translation_word_basic PASSED

========================= 16 passed in X.XXs =========================
```

### pytest Benefits
- **Individual Test Execution**: Run specific tests for focused debugging
- **Parallel Execution**: Faster test runs with `-n auto`
- **Better Output**: Cleaner, more detailed test reports
- **Context Efficiency**: Individual test files are 40-160 lines vs 418 lines

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

#### KiloCode Configuration (Recommended)

**Step 1**: Find your absolute paths and set up the virtual environment:
```bash
# Navigate to your mcp-proxy directory (replace with your actual path)
cd /absolute/path/to/your/translation-helps-mcp/mcp-proxy

# Activate virtual environment
. venv/bin/activate

# Note these paths for the configuration
pwd                # Current directory (use for 'cwd')
which python       # Python executable path (use for 'command')
```

**Step 2**: Add this configuration to your KiloCode MCP settings JSON:
```json
{
  "translation-helps-mcp-proxy": {
    "command": "/absolute/path/to/your/translation-helps-mcp/mcp-proxy/venv/bin/python",
    "args": ["mcp_proxy_server.py"],
    "cwd": "/absolute/path/to/your/translation-helps-mcp/mcp-proxy",
    "env": {
      "PYTHONPATH": "/absolute/path/to/your/translation-helps-mcp/mcp-proxy"
    }
  }
}
```

**Replace the paths above with your actual paths**:
- Replace `/absolute/path/to/your/translation-helps-mcp/mcp-proxy` with your real directory path
- The `command` should point to your venv's Python: `YOUR_PATH/venv/bin/python`
- All three path fields should use the same base directory

**Key Configuration Notes**:
- **`command`**: Use the **venv Python executable** (not system python)
- **`cwd`**: Absolute path to the mcp-proxy directory
- **`env.PYTHONPATH`**: Ensures Python can find the modules
- **Server name**: `translation-helps-mcp-proxy` (use this name in KiloCode)

#### Alternative: Generic MCP Client Configuration

For other MCP clients that don't support virtual environments well:
```json
{
  "translation-helps-mcp-proxy": {
    "command": "python",
    "args": ["mcp_proxy_server.py"],
    "cwd": "/absolute/path/to/mcp-proxy"
  }
}
```

#### Verification Steps

**Test the configuration**:
1. Save the JSON configuration in KiloCode
2. Restart KiloCode or reload MCP servers
3. In KiloCode, verify the server appears in the MCP tools list
4. Try calling a tool like `fetch_scripture` with `{"reference": "John 3:16"}`

**Expected behavior**:
- Server should connect without errors
- 12 tools should be available
- `fetch_scripture` should return John 3:16 text
- `fetch_translation_notes` should return translation notes

#### Troubleshooting KiloCode Integration

**If the server doesn't start**:
```bash
# Test manually first (replace with your actual path)
cd /absolute/path/to/your/translation-helps-mcp/mcp-proxy
. venv/bin/activate
python mcp_proxy_server.py --debug
```

**Common issues**:
- **Wrong Python path**: Ensure you're using `venv/bin/python`, not system python
- **Missing dependencies**: Run `pip install -r requirements.txt` in the venv
- **Path issues**: Use absolute paths for all directory references
- **Permissions**: Ensure the venv directory is readable

**Debug configuration in KiloCode**:
- Check KiloCode's MCP server logs for connection errors
- Verify the server name matches exactly (`translation-helps-mcp-proxy`)
- Ensure no other MCP servers are using the same name

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
- [x] Convert to pytest-based test suite for better CI/CD integration
- [ ] Add response caching for frequently called tools
- [ ] Support for additional MCP features (resources, prompts)
- [ ] Metrics and monitoring capabilities
- [ ] Rate limiting and request queuing

## 📝 License

This proxy server is provided as-is to enable compatibility with the translation-helps-mcp service.

---

**🎉 Production Ready** - The proxy server successfully bridges MCP clients with the upstream translation-helps-mcp server, with all tools working including Bible verse fetching via `fetch_scripture`.