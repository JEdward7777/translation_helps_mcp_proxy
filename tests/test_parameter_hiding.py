"""Test parameter hiding functionality for tool arguments."""

import pytest
from translation_helps_mcp_proxy.mcp_proxy_server import MCPProxyServer


@pytest.mark.asyncio
async def test_hide_language_and_organization_params():
    """Test that language and organization parameters can be hidden from tool schemas."""
    # Create proxy with parameter hiding enabled
    proxy = MCPProxyServer(verify_ssl=False, hidden_params=['language', 'organization'])
    
    try:
        # Get filtered tools
        tools = await proxy._get_filtered_tools()
        
        # Find fetch_translation_notes tool
        translation_notes_tool = None
        for tool in tools:
            if tool.name == 'fetch_translation_notes':
                translation_notes_tool = tool
                break
        
        assert translation_notes_tool is not None, "fetch_translation_notes tool should exist"
        
        # Verify the tool has an input schema
        assert hasattr(translation_notes_tool, 'inputSchema'), "Tool should have inputSchema"
        assert 'properties' in translation_notes_tool.inputSchema, "Schema should have properties"
        
        # Verify language and organization are NOT in the properties
        properties = translation_notes_tool.inputSchema['properties']
        assert 'language' not in properties, "language parameter should be hidden"
        assert 'organization' not in properties, "organization parameter should be hidden"
        
        # Verify reference is still present (not hidden)
        assert 'reference' in properties, "reference parameter should still be present"
        
        # Verify required list doesn't include hidden params
        if 'required' in translation_notes_tool.inputSchema:
            required = translation_notes_tool.inputSchema['required']
            assert 'language' not in required, "language should not be in required list"
            assert 'organization' not in required, "organization should not be in required list"
        
    finally:
        if not proxy.client.is_closed:
            await proxy.client.aclose()


@pytest.mark.asyncio
async def test_no_parameter_hiding_by_default():
    """Test that without parameter hiding, all parameters are present."""
    # Create proxy WITHOUT parameter hiding (default behavior)
    proxy = MCPProxyServer(verify_ssl=False)
    
    try:
        tools = await proxy._get_filtered_tools()
        
        # Find fetch_translation_notes tool
        translation_notes_tool = None
        for tool in tools:
            if tool.name == 'fetch_translation_notes':
                translation_notes_tool = tool
                break
        
        assert translation_notes_tool is not None, "fetch_translation_notes tool should exist"
        
        # Verify ALL parameters are present when hiding is disabled
        properties = translation_notes_tool.inputSchema['properties']
        assert 'reference' in properties, "reference parameter should be present"
        assert 'language' in properties, "language parameter should be present (not hidden)"
        assert 'organization' in properties, "organization parameter should be present (not hidden)"
        
    finally:
        if not proxy.client.is_closed:
            await proxy.client.aclose()


@pytest.mark.asyncio
async def test_hide_params_affects_multiple_tools():
    """Test that hidden params affect all tools that have those parameters."""
    proxy = MCPProxyServer(verify_ssl=False, hidden_params=['language', 'organization'])
    
    try:
        tools = await proxy._get_filtered_tools()
        
        # Check multiple tools that should have language/organization
        tools_to_check = ['fetch_translation_notes', 'fetch_scripture', 'fetch_translation_questions']
        
        for tool_name in tools_to_check:
            tool = None
            for t in tools:
                if t.name == tool_name:
                    tool = t
                    break
            
            if tool is None:
                continue  # Skip if tool doesn't exist
            
            properties = tool.inputSchema.get('properties', {})
            
            # Verify hidden params are not present
            assert 'language' not in properties, f"{tool_name} should not have language parameter"
            assert 'organization' not in properties, f"{tool_name} should not have organization parameter"
        
    finally:
        if not proxy.client.is_closed:
            await proxy.client.aclose()


@pytest.mark.asyncio
async def test_hide_single_parameter():
    """Test hiding only a single parameter."""
    proxy = MCPProxyServer(verify_ssl=False, hidden_params=['language'])
    
    try:
        tools = await proxy._get_filtered_tools()
        
        translation_notes_tool = None
        for tool in tools:
            if tool.name == 'fetch_translation_notes':
                translation_notes_tool = tool
                break
        
        assert translation_notes_tool is not None
        
        properties = translation_notes_tool.inputSchema['properties']
        
        # Only language should be hidden
        assert 'language' not in properties, "language should be hidden"
        assert 'organization' in properties, "organization should still be present"
        assert 'reference' in properties, "reference should be present"
        
    finally:
        if not proxy.client.is_closed:
            await proxy.client.aclose()


@pytest.mark.asyncio
async def test_empty_hidden_params_list():
    """Test that empty hidden params list doesn't hide anything."""
    proxy = MCPProxyServer(verify_ssl=False, hidden_params=[])
    
    try:
        tools = await proxy._get_filtered_tools()
        
        translation_notes_tool = None
        for tool in tools:
            if tool.name == 'fetch_translation_notes':
                translation_notes_tool = tool
                break
        
        assert translation_notes_tool is not None
        
        properties = translation_notes_tool.inputSchema['properties']
        
        # All parameters should be present
        assert 'language' in properties, "language should be present"
        assert 'organization' in properties, "organization should be present"
        assert 'reference' in properties, "reference should be present"
        
    finally:
        if not proxy.client.is_closed:
            await proxy.client.aclose()


@pytest.mark.asyncio
async def test_hidden_params_case_sensitive():
    """Test that parameter hiding is case-sensitive."""
    proxy = MCPProxyServer(verify_ssl=False, hidden_params=['Language', 'ORGANIZATION'])
    
    try:
        tools = await proxy._get_filtered_tools()
        
        translation_notes_tool = None
        for tool in tools:
            if tool.name == 'fetch_translation_notes':
                translation_notes_tool = tool
                break
        
        assert translation_notes_tool is not None
        
        properties = translation_notes_tool.inputSchema['properties']
        
        # Parameters should NOT be hidden because case doesn't match
        assert 'language' in properties, "language should be present (case mismatch)"
        assert 'organization' in properties, "organization should be present (case mismatch)"
        
    finally:
        if not proxy.client.is_closed:
            await proxy.client.aclose()