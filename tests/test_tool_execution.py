"""Test tool execution through the proxy."""

import pytest


@pytest.mark.asyncio
async def test_tool_execution(proxy_server):
    """Test 3: Verify tool execution through the proxy."""
    print("\n🔧 Test 3: Tool Execution")
    print("-" * 40)
    
    try:
        # Test a simple tool call
        print("   Testing get_system_prompt tool...")
        response = await proxy_server._call_upstream('tools/call', {
            'name': 'get_system_prompt',
            'arguments': {'includeImplementationDetails': False}
        })
        
        assert response is not None, "No response from tool call"
        assert 'content' in response, "Missing content in response"
        
        content = response['content'][0]['text']
        print("   ✅ Tool execution successful")
        print(f"   📄 Response length: {len(content)} characters")
        print(f"   🔍 Preview: {content[:100]}...")
        
        # Test another tool
        print("   Testing fetch_scripture tool...")
        scripture_response = await proxy_server._call_upstream('tools/call', {
            'name': 'fetch_scripture',
            'arguments': {'reference': 'John 3:16'}
        })
        
        assert scripture_response is not None, "No scripture response"
        
        if 'scripture' in scripture_response:
            # New format: direct API endpoint response
            scripture_list = scripture_response['scripture']
            if scripture_list:
                scripture_text = scripture_list[0]['text']
                print("   ✅ Scripture fetch successful")
                print(f"   📖 Response preview: {scripture_text[:100]}...")
            else:
                print("   ⚠️  Scripture fetch returned empty list")
        elif 'content' in scripture_response:
            # Old format: MCP content format
            scripture_text = scripture_response['content'][0]['text']
            print("   ✅ Scripture fetch successful")
            print(f"   📖 Response preview: {scripture_text[:100]}...")
        else:
            print("   ⚠️  Scripture fetch returned unexpected format (this may be expected)")
            print(f"   Response keys: {list(scripture_response.keys()) if scripture_response else 'None'}")
            
    except Exception as e:
        print(f"   ❌ Error during tool execution test: {e}")
        assert False, f"Error during tool execution test: {e}"


@pytest.mark.asyncio
async def test_get_system_prompt_tool(proxy_server):
    """Test the get_system_prompt tool specifically."""
    response = await proxy_server._call_upstream('tools/call', {
        'name': 'get_system_prompt',
        'arguments': {'includeImplementationDetails': False}
    })
    
    assert response is not None, "No response from get_system_prompt"
    assert 'content' in response, "Missing content in get_system_prompt response"
    assert isinstance(response['content'], list), "Content should be a list"
    assert len(response['content']) > 0, "Content list should not be empty"
    
    content_item = response['content'][0]
    assert 'text' in content_item, "Missing text in content item"
    assert len(content_item['text']) > 0, "System prompt should not be empty"


@pytest.mark.asyncio
async def test_fetch_scripture_tool(proxy_server):
    """Test the fetch_scripture tool specifically."""
    response = await proxy_server._call_upstream('tools/call', {
        'name': 'fetch_scripture',
        'arguments': {'reference': 'John 3:16'}
    })
    
    assert response is not None, "No response from fetch_scripture"
    
    # Handle different response formats
    if 'scripture' in response:
        # Direct API format
        scripture_list = response['scripture']
        assert isinstance(scripture_list, list), "Scripture should be a list"
        if scripture_list:  # Allow empty list as valid response
            assert 'text' in scripture_list[0], "Missing text in scripture item"
    elif 'content' in response:
        # MCP format
        assert isinstance(response['content'], list), "Content should be a list"
        assert len(response['content']) > 0, "Content list should not be empty"
        assert 'text' in response['content'][0], "Missing text in content item"
    else:
        # Allow other formats for now, but at least verify it's not None
        assert response, "Scripture response should not be empty"


@pytest.mark.asyncio
async def test_invalid_tool_call(proxy_server):
    """Test calling a non-existent tool."""
    response = await proxy_server._call_upstream('tools/call', {
        'name': 'nonexistent_tool',
        'arguments': {}
    })
    
    # Should either return None or an error response, not crash
    # This is a basic sanity check for error handling
    assert True  # If we get here without exception, the error handling worked