"""Test upstream server connectivity and tool discovery."""

import pytest


@pytest.mark.asyncio
async def test_upstream_connectivity(proxy_server):
    """Test 1: Verify upstream server connectivity and tool discovery."""
    print("🔗 Test 1: Upstream Server Connectivity")
    print("-" * 40)
    
    try:
        # Test basic connectivity
        connected = await proxy_server.test_connection()
        if not connected:
            print("   ❌ Failed to connect to upstream server")
            assert False, "Failed to connect to upstream server"
        
        print("   ✅ Connected to upstream server")
        
        # Test tools discovery
        response = await proxy_server._call_upstream('tools/list', {})
        if response and 'tools' in response:
            tool_count = len(response['tools'])
            print(f"   ✅ Discovered {tool_count} tools from upstream")
            
            # Show first few tools
            print("   📋 Available tools:")
            for i, tool in enumerate(response['tools'][:3]):
                print(f"      {i+1}. {tool['name']}: {tool['description'][:50]}...")
            if tool_count > 3:
                print(f"      ... and {tool_count - 3} more tools")
            
            assert tool_count > 0, "No tools discovered"
            assert tool_count >= 12, f"Expected at least 12 tools, got {tool_count}"
        else:
            print("   ❌ Failed to discover tools from upstream")
            assert False, "Failed to discover tools from upstream"
            
    except Exception as e:
        print(f"   ❌ Error during connectivity test: {e}")
        assert False, f"Error during connectivity test: {e}"


@pytest.mark.asyncio
async def test_tools_list_format(proxy_server):
    """Test that tools list has correct format."""
    response = await proxy_server._call_upstream('tools/list', {})
    
    assert response is not None, "No response from upstream"
    assert 'tools' in response, "Response missing 'tools' key"
    
    tools = response['tools']
    assert isinstance(tools, list), "Tools should be a list"
    assert len(tools) > 0, "Tools list should not be empty"
    
    # Check first tool has required fields
    first_tool = tools[0]
    required_fields = ['name', 'description']
    for field in required_fields:
        assert field in first_tool, f"Tool missing required field: {field}"
        assert first_tool[field], f"Tool field {field} should not be empty"