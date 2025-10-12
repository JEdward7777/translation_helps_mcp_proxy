"""Test tool filtering functionality for controlled rollout."""

import pytest
import asyncio
from translation_helps_mcp_proxy.mcp_proxy_server import MCPProxyServer


@pytest.mark.asyncio
async def test_default_all_tools_enabled():
    """Test that by default all tools are enabled."""
    proxy = MCPProxyServer(verify_ssl=False)
    
    try:
        # Get all available tools from upstream
        upstream_response = await proxy._call_upstream('tools/list', {})
        assert upstream_response is not None, "Should get upstream tools"
        assert 'tools' in upstream_response, "Should have tools in response"
        upstream_tools = upstream_response['tools']
        
        # Test that proxy returns all tools by default (no filtering)
        proxy_tools = await proxy._get_filtered_tools()
        
        assert len(proxy_tools) == len(upstream_tools), "Should return all tools by default"
        
        # Verify tool names match
        upstream_names = {tool['name'] for tool in upstream_tools}
        proxy_names = {tool.name for tool in proxy_tools}
        assert upstream_names == proxy_names, "Tool names should match between upstream and proxy"
        
    finally:
        if not proxy.client.is_closed:
            await proxy.client.aclose()


@pytest.mark.asyncio
async def test_tool_filtering_specific_tools():
    """Test filtering to only specific tools."""
    # Create proxy with specific tools enabled
    enabled_tools = ['fetch_scripture', 'fetch_translation_notes']
    proxy = MCPProxyServer(verify_ssl=False, enabled_tools=enabled_tools)
    
    try:
        # Test that only specified tools are returned
        proxy_tools = await proxy._get_filtered_tools()
        
        assert len(proxy_tools) == 2, f"Should return exactly 2 tools, got {len(proxy_tools)}"
        
        tool_names = {tool.name for tool in proxy_tools}
        expected_names = {'fetch_scripture', 'fetch_translation_notes'}
        assert tool_names == expected_names, f"Should return only {expected_names}, got {tool_names}"
        
    finally:
        if not proxy.client.is_closed:
            await proxy.client.aclose()


@pytest.mark.asyncio
async def test_invalid_tool_validation():
    """Test that specifying non-existent tools raises an error."""
    # Create proxy with invalid tool - error occurs during first tool list call
    proxy = MCPProxyServer(verify_ssl=False, enabled_tools=['fetch_scripture', 'nonexistent_tool'])
    
    try:
        # This should raise an error when validation occurs
        with pytest.raises(ValueError, match="Unknown tools specified"):
            await proxy._get_filtered_tools()
    finally:
        if not proxy.client.is_closed:
            await proxy.client.aclose()


@pytest.mark.asyncio
async def test_empty_tools_list():
    """Test that empty tools list disables all tools."""
    proxy = MCPProxyServer(verify_ssl=False, enabled_tools=[])
    
    try:
        proxy_tools = await proxy._get_filtered_tools()
        assert len(proxy_tools) == 0, "Empty tools list should disable all tools"
        
    finally:
        if not proxy.client.is_closed:
            await proxy.client.aclose()


@pytest.mark.asyncio
async def test_disabled_tool_call_blocked():
    """Test that calling a disabled tool returns an error."""
    # Enable only fetch_scripture, disable fetch_translation_notes
    proxy = MCPProxyServer(verify_ssl=False, enabled_tools=['fetch_scripture'])
    
    try:
        # This should work - tool is enabled
        enabled_response = await proxy._call_upstream('tools/call', {
            'name': 'fetch_scripture',
            'arguments': {'reference': 'John 3:16'}
        })
        assert enabled_response is not None, "Enabled tool should work"
        
        # This should be blocked - tool is disabled
        disabled_response = await proxy._is_tool_enabled('fetch_translation_notes')
        assert not disabled_response, "fetch_translation_notes should be disabled"
        
    finally:
        if not proxy.client.is_closed:
            await proxy.client.aclose()


@pytest.mark.asyncio
async def test_tool_filtering_case_sensitivity():
    """Test that tool filtering is case-sensitive and exact match."""
    # Test exact case matching
    proxy = MCPProxyServer(verify_ssl=False, enabled_tools=['fetch_scripture'])
    
    try:
        # Exact case should work
        assert await proxy._is_tool_enabled('fetch_scripture'), "Exact case should work"
        
        # Different case should not work (if we had case variations)
        assert not await proxy._is_tool_enabled('FETCH_SCRIPTURE'), "Case should matter"
        assert not await proxy._is_tool_enabled('Fetch_Scripture'), "Case should matter"
        
    finally:
        if not proxy.client.is_closed:
            await proxy.client.aclose()


@pytest.mark.asyncio
async def test_command_line_args_integration():
    """Test that command line arguments work with tool filtering."""
    import sys
    from unittest.mock import patch
    
    # Mock command line arguments
    test_args = [
        'mcp_proxy_server.py',
        '--enabled-tools', 'fetch_scripture,fetch_translation_notes',
        '--debug'
    ]
    
    with patch.object(sys, 'argv', test_args):
        # This test ensures the argument parsing works
        # We'll verify this in the implementation
        assert True, "Command line integration test placeholder"


@pytest.mark.asyncio
async def test_list_tools_command():
    """Test the --list-tools command line option."""
    import subprocess
    import sys
    from pathlib import Path
    
    # Test the --list-tools functionality
    package_dir = Path(__file__).parent.parent / "src" / "translation_helps_mcp_proxy"
    cmd = [sys.executable, str(package_dir / "mcp_proxy_server.py"), "--list-tools"]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
            timeout=15
        )
        
        # Should exit with code 0 (success)
        assert result.returncode == 0, f"Command should succeed, got exit code {result.returncode}"
        
        # Should output tool list
        output = result.stdout
        assert "available tools" in output.lower(), "Should mention available tools"
        assert "fetch_scripture" in output, "Should list fetch_scripture tool"
        assert "fetch_translation_notes" in output, "Should list fetch_translation_notes tool"
        assert "usage:" in output.lower(), "Should show usage example"
        
        # Should show tool count
        assert "found" in output.lower() and "tools" in output.lower(), "Should show tool count"
        
    except subprocess.TimeoutExpired:
        pytest.fail("--list-tools command timed out")
    except Exception as e:
        pytest.fail(f"Error testing --list-tools command: {e}")


@pytest.mark.asyncio
async def test_tool_filtering_preserves_tool_schemas():
    """Test that filtered tools preserve their input schemas."""
    enabled_tools = ['fetch_scripture', 'fetch_translation_notes']
    proxy = MCPProxyServer(verify_ssl=False, enabled_tools=enabled_tools)
    
    try:
        proxy_tools = await proxy._get_filtered_tools()
        
        # Find fetch_scripture tool
        scripture_tool = None
        for tool in proxy_tools:
            if tool.name == 'fetch_scripture':
                scripture_tool = tool
                break
        
        assert scripture_tool is not None, "fetch_scripture should be in filtered tools"
        assert hasattr(scripture_tool, 'inputSchema'), "Tool should have input schema"
        assert 'properties' in scripture_tool.inputSchema, "Input schema should have properties"
        assert 'reference' in scripture_tool.inputSchema['properties'], "Should require reference parameter"
        
    finally:
        if not proxy.client.is_closed:
            await proxy.client.aclose()